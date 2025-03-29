import os
import io
import tempfile
import humanize
from pyrogram import Client, filters, enums
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.utils import ImageReader
from pdf2image import convert_from_path
from PIL import Image
from pyrogram.types import Message
from config import LOG_CHANNEL
from helper.database import db
from plugins.Fsub import auth_check
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pdf_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def create_4up_pdf(input_path: str, output_path: str):
    """Create a 4-up PDF with detailed logging"""
    start_time = datetime.now()
    logger.info(f"Starting 4-up PDF creation for {input_path}")
    
    try:
        # Verify the input file exists
        if not os.path.exists(input_path):
            logger.error(f"Input file not found: {input_path}")
            return False

        # Convert PDF to images first
        images = convert_from_path(input_path, dpi=300)
        total_pages = len(images)
        logger.info(f"Converted PDF to {total_pages} images")

        writer = PdfWriter()
        
        # Landscape A4 dimensions
        page_width, page_height = landscape(A4)
        margin = 20
        content_width = page_width - 2 * margin
        content_height = page_height - 2 * margin
        slide_width = content_width / 2
        slide_height = content_height / 2
        
        logger.debug(f"Using page size: {page_width}x{page_height} with {margin}pt margins")

        processed_pages = 0
        for i in range(0, total_pages, 4):
            batch_start = datetime.now()
            current_batch = images[i:i+4]
            batch_size = len(current_batch)
            
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=(page_width, page_height))
            
            # Positions for 2x2 grid
            positions = [
                (margin, margin + slide_height),  # Top-left
                (margin + slide_width, margin + slide_height),  # Top-right
                (margin, margin),                 # Bottom-left
                (margin + slide_width, margin)    # Bottom-right
            ]
            
            # Draw each slide
            for img, pos in zip(current_batch, positions):
                try:
                    img_bytes = io.BytesIO()
                    img.save(img_bytes, format='JPEG')
                    img_bytes.seek(0)
                    can.drawImage(
                        ImageReader(img_bytes),
                        pos[0],
                        pos[1],
                        width=slide_width,
                        height=slide_height,
                        preserveAspectRatio=True,
                        anchor='nw'
                    )
                except Exception as e:
                    logger.error(f"Error processing page {i+1}: {str(e)}")
                    continue
            
            can.save()
            packet.seek(0)
            
            # Add combined page to output
            try:
                combined_pdf = PdfReader(packet)
                if len(combined_pdf.pages) > 0:
                    writer.add_page(combined_pdf.pages[0])
                    processed_pages += batch_size
                    logger.debug(
                        f"Processed batch {i//4 + 1}: Pages {i+1}-{i+batch_size} "
                        f"(took {(datetime.now() - batch_start).total_seconds():.2f}s)"
                    )
            except Exception as e:
                logger.error(f"Failed to add combined page: {str(e)}")

        # Write output PDF
        with open(output_path, "wb") as f:
            writer.write(f)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"Successfully created 4-up PDF: {output_path}\n"
            f"Processed {processed_pages}/{total_pages} pages in {processing_time:.2f} seconds "
            f"({processed_pages/processing_time:.1f} pages/sec)"
        )
        return True

    except Exception as e:
        logger.error(f"Failed to create 4-up PDF: {str(e)}", exc_info=True)
        return False

@Client.on_message(filters.command(["4up"]) & filters.private)
@auth_check
async def handle_4up_command(client: Client, message: Message):
    """Processes a PDF into 4-slides-per-page format."""
    user_id = message.from_user.id
    logger.info(f"Received /4up command from user {user_id}")

    # Ensure the command is a reply to a document
    if not message.reply_to_message or not message.reply_to_message.document:
        logger.warning(f"User {user_id} sent /4up without replying to a document")
        await message.reply_text("❌ Please reply to a **PDF file** with /4up.")
        return
    
    doc = message.reply_to_message.document
    if doc.mime_type != "application/pdf":
        logger.warning(f"User {user_id} sent non-PDF file: {doc.file_name} ({doc.mime_type})")
        await message.reply_text("❌ Only **PDF files** are supported for 4up conversion.")
        return

    logger.info(f"Processing PDF: {doc.file_name} (Size: {humanize.naturalsize(doc.file_size)})")
    progress_msg = await message.reply_text("🔄 Processing your 4-up PDF...")

    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, "input.pdf")
        output_path = os.path.join(temp_dir, "4up_output.pdf")
        thumb_path = None

        try:
            # Download the PDF
            dl_start = datetime.now()
            await client.download_media(
                message.reply_to_message.document.file_id,
                file_name=input_path
            )
            dl_time = (datetime.now() - dl_start).total_seconds()
            logger.info(f"Download completed in {dl_time:.2f}s")

            # Verify file downloaded correctly
            if not os.path.exists(input_path) or os.path.getsize(input_path) == 0:
                logger.error("Downloaded file is missing or empty!")
                await progress_msg.edit_text("❌ Failed to download the PDF.")
                return

            # Process the PDF (Create 4-up format)
            process_start = datetime.now()
            success = await create_4up_pdf(input_path, output_path)

            if not success or not os.path.exists(output_path):
                logger.error(f"4-up creation failed for user {user_id}")
                await progress_msg.edit_text("❌ Failed to process PDF.")
                return
            
            process_time = (datetime.now() - process_start).total_seconds()
            logger.info(f"PDF processing completed in {process_time:.2f}s")

            # Fetch custom thumbnail (if available)
            try:
                thumb = await db.get_thumbnail(user_id)
                if thumb:
                    thumb_path = await client.download_media(thumb)
                    logger.debug(f"Using custom thumbnail for user {user_id}")
            except Exception as e:
                logger.warning(f"Thumbnail error: {str(e)}")

            # Send the processed PDF back to the user
            await message.reply_document(
                document=output_path,
                thumb=thumb_path,
                caption="✅ Your **4-slides-per-page PDF** (Landscape A4)",
            )
            logger.info(f"Successfully sent result to user {user_id}")

            # Log to admin channel
            try:
                await client.send_document(
                    LOG_CHANNEL,
                    document=output_path,
                    caption=f"4-up PDF created by {message.from_user.mention}\n"
                            f"User ID: {user_id}\n"
                            f"Original: {doc.file_name} ({humanize.naturalsize(doc.file_size)})\n"
                            f"Processing time: {process_time:.1f}s"
                )
            except Exception as e:
                logger.error(f"Failed to log to channel: {str(e)}")

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            await progress_msg.edit_text("❌ An unexpected error occurred.")
        finally:
            if thumb_path and os.path.exists(thumb_path):
                os.remove(thumb_path)
            await progress_msg.delete()
            logger.debug("Cleaned up temporary resources")
