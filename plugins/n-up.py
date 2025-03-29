import os
import io
import tempfile
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.utils import ImageReader
from pyrogram import filters
from pyrogram.types import Message
from config import LOG_CHANNEL
from helper.database import db
from plugins.Fsub import auth_check
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
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
        reader = PdfReader(input_path)
        writer = PdfWriter()
        total_pages = len(reader.pages)
        logger.info(f"Input PDF loaded with {total_pages} pages")

        page_width, page_height = landscape(A4)
        margin = 20
        logger.debug(f"Using page size: {page_width}x{page_height} with {margin}pt margins")

        processed_pages = 0
        for i in range(0, total_pages, 4):
            batch_start = datetime.now()
            current_batch = reader.pages[i:i+4]
            batch_size = len(current_batch)
            
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=(page_width, page_height))
            
            # [Previous position and drawing code remains the same...]
            
            can.save()
            packet.seek(0)
            writer.add_page(PdfReader(packet).pages[0])
            processed_pages += batch_size
            
            logger.debug(
                f"Processed batch {i//4 + 1}: "
                f"Pages {i+1}-{i+batch_size} "
                f"(took {(datetime.now() - batch_start).total_seconds():.2f}s)"
            )

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
    """Enhanced with detailed logging"""
    user_id = message.from_user.id
    logger.info(f"Received /4up command from user {user_id}")
    
    if not message.reply_to_message:
        logger.warning(f"User {user_id} sent /4up without replying to a message")
        await message.reply_text("🔹 Please reply to a PDF file with /4up command")
        return
    
    if not message.reply_to_message.document:
        logger.warning(f"User {user_id} replied to non-document message")
        await message.reply_text("❌ Please reply to a PDF document")
        return
    
    doc = message.reply_to_message.document
    if doc.mime_type != "application/pdf":
        logger.warning(f"User {user_id} sent non-PDF file: {doc.file_name} ({doc.mime_type})")
        await message.reply_text("❌ Only PDF files are supported for 4up conversion")
        return
    
    logger.info(f"Processing PDF: {doc.file_name} ({humanize.naturalsize(doc.file_size)})")
    progress_msg = await message.reply_text("🔄 Processing your 4-up PDF...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, "input.pdf")
        output_path = os.path.join(temp_dir, "4up_output.pdf")
        
        try:
            # Download logging
            dl_start = datetime.now()
            await client.download_media(doc.file_id, file_name=input_path)
            dl_time = (datetime.now() - dl_start).total_seconds()
            logger.info(f"Download completed in {dl_time:.2f}s ({humanize.naturalsize(doc.file_size/dl_time)}/s)")
            
            # Processing
            process_start = datetime.now()
            success = await create_4up_pdf(input_path, output_path)
            
            if not success:
                logger.error(f"4-up creation failed for user {user_id}")
                await progress_msg.edit_text("❌ Failed to create 4-up PDF")
                return
            
            process_time = (datetime.now() - process_start).total_seconds()
            logger.info(f"PDF processing completed in {process_time:.2f}s")
            
            # Thumbnail handling
            thumb_path = None
            if await db.get_thumbnail(user_id):
                try:
                    thumb_path = await client.download_media(await db.get_thumbnail(user_id))
                    logger.debug(f"Using custom thumbnail for user {user_id}")
                except Exception as e:
                    logger.warning(f"Failed to download thumbnail for user {user_id}: {str(e)}")
            
            # Send result
            await message.reply_document(
                document=output_path,
                thumb=thumb_path,
                caption="✅ Your 4-slides-per-page PDF (Landscape A4)"
            )
            logger.info(f"Successfully sent result to user {user_id}")
            
            # Log to channel
            log_caption = (
                f"📑 4-up PDF created\n"
                f"👤 User: {message.from_user.mention}\n"
                f"🆔 ID: {user_id}\n"
                f"⏱️ Process time: {process_time:.1f}s\n"
                f"📊 Original: {doc.file_name} ({humanize.naturalsize(doc.file_size)})\n"
                f"🔄 Converted: {humanize.naturalsize(os.path.getsize(output_path))}"
            )
            await client.send_document(LOG_CHANNEL, document=output_path, caption=log_caption)
            
        except Exception as e:
            logger.error(f"Unexpected error processing 4-up for user {user_id}: {str(e)}", exc_info=True)
            await progress_msg.edit_text("❌ An unexpected error occurred")
        finally:
            if thumb_path and os.path.exists(thumb_path):
                os.remove(thumb_path)
            await progress_msg.delete()
            logger.debug("Cleaned up temporary resources")

