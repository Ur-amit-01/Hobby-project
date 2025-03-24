import os
import tempfile
import humanize
from pyrogram import Client, filters
from pyrogram.types import Message, ReplyKeyboardRemove
from pyrogram.errors import BadRequest

# Handler for /compress command
@Client.on_message(filters.command("compress") & filters.private)
async def compress_pdf(client: Client, message: Message):
    # Ask user to send a PDF file
    await message.reply_text(
        "📁 Please send me the PDF file you want to compress",
        reply_markup=ReplyKeyboardRemove()
    )
    
    # Wait for the document
    try:
        pdf_msg = await client.listen(message.chat.id, filters.document, timeout=30)
    except TimeoutError:
        await message.reply_text("⏰ You took too long to send the PDF. Please try again.")
        return
    
    if not pdf_msg.document.file_name.lower().endswith(".pdf"):
        await message.reply_text("❌ That's not a PDF file. Please send a PDF.")
        return
    
    # Download the PDF
    await message.reply_text("⚙️ Compressing your PDF file...")
    
    with tempfile.NamedTemporaryFile(suffix=".pdf") as input_file:
        # Download the PDF
        await client.download_media(
            pdf_msg.document,
            file_name=input_file.name
        )
        
        # Prepare output file
        with tempfile.NamedTemporaryFile(suffix=".pdf") as output_file:
            # Ghostscript command for compression
            command = (
                f"gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 "
                f"-dPDFSETTINGS=/default -dNOPAUSE -dQUIET -dBATCH "
                f'-sOutputFile="{output_file.name}" "{input_file.name}"'
            )
            
            # Execute the command
            if os.system(command) == 0:  # Success
                # Get file sizes
                old_size = os.path.getsize(input_file.name)
                new_size = os.path.getsize(output_file.name)
                
                # Send result with compression info
                await message.reply_text(
                    f"✅ File size reduced by <b>{1 - new_size/old_size:.0%}</b>\n"
                    f"📊 From <b>{humanize.naturalsize(old_size)}</b> "
                    f"to <b>{humanize.naturalsize(new_size)}</b>",
                    parse_mode="html"
                )
                
                # Send the compressed file
                await client.send_document(
                    chat_id=message.chat.id,
                    document=output_file.name,
                    file_name=f"compressed_{pdf_msg.document.file_name}",
                    caption="Here's your compressed PDF file"
                )
            else:
                await message.reply_text("❌ Failed to compress the PDF. Please try another file.")
