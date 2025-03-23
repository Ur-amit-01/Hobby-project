import os
import re
import time
import logging
import tempfile
import asyncio
import humanize
import requests
from PIL import Image
from pyrogram import Client, filters
from PyPDF2 import PdfMerger, PdfReader
from PyPDF2.errors import PdfReadError
from pyrogram.types import Message, ForceReply
from config import LOG_CHANNEL
from helper.database import db
from plugins.Fsub import auth_check

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 350 * 1024 * 1024  # 350MB

user_file_metadata = {}  # Store metadata for each user's files
user_states = {}  # Track user states
pending_filename_requests = {}  # Track pending filename requests

async def reset_user_state(user_id: int):
    await asyncio.sleep(300)  # 5 minutes
    if user_id in user_file_metadata:
        user_file_metadata.pop(user_id, None)
        pending_filename_requests.pop(user_id, None)
        user_states.pop(user_id, None)
        logger.info(f"Reset state for user {user_id} due to inactivity.")

async def show_dual_progress_bar(progress_message, merge_current, merge_total, download_current, download_total, start_time, bar_length=10):
    """
    Shows both merge progress and download progress in a single message.
    """
    # Merge progress bar
    merge_progress = min(merge_current / merge_total, 1.0)
    merge_filled_length = int(bar_length * merge_progress)
    merge_bar = "●" * merge_filled_length + "○" * (bar_length - merge_filled_length)
    merge_percentage = int(merge_progress * 100)

    # Download progress bar
    elapsed_time = time.time() - start_time
    download_speed = download_current / elapsed_time if elapsed_time > 0 else 0  # Bytes per second
    download_progress = min(download_current / download_total, 1.0)
    download_percentage = int(download_progress * 100)
    remaining_time = (download_total - download_current) / download_speed if download_speed > 0 else 0  # Remaining time in seconds

    # Format the message
    text = (
        f"**Merging... 📃 + 📃**\n"
        f"`[{merge_bar}]` {merge_percentage}% ({merge_current}/{merge_total})\n\n"
        f"**╭━━━━❰ Downloading... ❱━➣**\n"
        f"**┣⪼ 🗂️ : {humanize.naturalsize(download_current)} | {humanize.naturalsize(download_total)}**\n"
        f"**┣⪼ ⏳️ : {download_percentage}%\n"
        f"**┣⪼ 🚀 : {humanize.naturalsize(download_speed)}/s**\n"
        f"**┣⪼ ⏱️ : {humanize.precisedelta(remaining_time)}**\n"
        f"**╰━━━━━━━━━━━━━━━➣**"
    )
    await progress_message.edit_text(text)

async def start_file_collection(client: Client, message: Message):
    user_id = message.from_user.id
    user_file_metadata[user_id] = []  # Reset file list for the user
    user_states[user_id] = "collecting_files"  # Set user state
    await message.reply_text(
        "**📤 ɴᴏᴡ ꜱᴇɴᴅ ʏᴏᴜʀ ғɪʟᴇs ɪɴ sᴇǫᴜᴇɴᴄᴇ !! 🧾**"
    )
    # Start a timer to reset the state after 5 minutes
    asyncio.create_task(reset_user_state(user_id))

async def handle_pdf_metadata(client: Client, message: Message):
    user_id = message.from_user.id

    # Only accept PDFs if the user has started the merge process
    if user_id not in user_states or user_states[user_id] != "collecting_files":
        return

    if message.document.mime_type != "application/pdf":
        await message.reply_text("❌ This is not a valid PDF file. Please send a PDF 📑.")
        return

    if len(user_file_metadata[user_id]) >= 20:
        await message.reply_text("⚠️ You can merge only 20 files at once. Type /done ✅ to merge them.")
        return

    if message.document.file_size > MAX_FILE_SIZE:
        await message.reply_text("🚫 File size is too large! Please send a file under 350MB.")
        return

    user_file_metadata[user_id].append(
        {
            "type": "pdf",
            "file_id": message.document.file_id,
            "file_name": message.document.file_name,
        }
    )
    await message.reply_text(
        f"•**ᴛᴏᴛᴀʟ ꜰɪʟᴇꜱ: {len(user_file_metadata[user_id])} 📄**\n"
        "•**/done: ᴛᴏ ᴍᴇʀɢᴇ ᴀʟʟ ꜰɪʟᴇꜱ ✅**"
    )

async def handle_image_metadata(client: Client, message: Message):
    user_id = message.from_user.id

    # Only accept images if the user has started the merge process
    if user_id not in user_states or user_states[user_id] != "collecting_files":
        return

    user_file_metadata[user_id].append(
        {
            "type": "image",
            "file_id": message.photo.file_id,
            "file_name": f"photo_{len(user_file_metadata[user_id]) + 1}.jpg",
        }
    )
    await message.reply_text(
        f"•**ᴛᴏᴛᴀʟ ɪᴍᴀɢᴇꜱ: {len(user_file_metadata[user_id])} 🖼️\n"
        "•**/done: ᴛᴏ ᴍᴇʀɢᴇ ᴀʟʟ ɪᴍᴀɢᴇꜱ ✅**"
    )

async def merge_files(client: Client, message: Message):
    user_id = message.from_user.id

    if user_id not in user_file_metadata or not user_file_metadata[user_id]:
        await message.reply_text("**⚠️ Yᴏᴜ ʜᴀᴠᴇɴ'ᴛ ᴀᴅᴅᴇᴅ ᴀɴʏ ғɪʟᴇs ʏᴇᴛ. Usᴇ /merge ᴛᴏ sᴛᴀʀᴛ.**")
        return

    # Ask for the filename using Force Reply
    await message.reply_text(
        "**✍️ Type a name for your merged PDF 📄.**",
        reply_markup=ForceReply(selective=True)  # Force Reply to this specific message
    )
    user_states[user_id] = "waiting_for_filename"  # Set user state

async def handle_filename(client: Client, message: Message):
    user_id = message.from_user.id

    # Check if the reply is to the bot's Force Reply message
    if (
        user_id in user_states
        and user_states[user_id] == "waiting_for_filename"
        and message.reply_to_message  # Ensure it's a reply
        and message.reply_to_message.from_user.is_self  # Ensure it's a reply to the bot's message
    ):
        custom_filename = message.text.strip()

        if not custom_filename:
            await message.reply_text("❌ Filename cannot be empty. Please try again.")
            return

        # Check if the filename contains a thumbnail link
        match = re.match(r"(.*)\s*-t\s*(https?://\S+)", custom_filename)
        if match:
            filename_without_thumbnail = match.group(1).strip()
            thumbnail_link = match.group(2).strip()

            # Validate the thumbnail link
            try:
                response = requests.get(thumbnail_link, timeout=10)
                if response.status_code != 200:
                    await message.reply_text("❌ Failed to fetch the image. Please provide a valid thumbnail link.")
                    return

                # Save the image to a temporary file
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_thumbnail:
                    temp_thumbnail.write(response.content)
                    thumbnail_path = temp_thumbnail.name

                # Process the thumbnail (resize and convert to JPEG)
                Image.open(thumbnail_path).convert("RGB").save(thumbnail_path)
                img = Image.open(thumbnail_path)
                img.resize((320, 320))
                img.save(thumbnail_path, "JPEG")

            except Exception as e:
                await message.reply_text(f"❌ Error while downloading or processing the thumbnail: {e}")
                return

        else:
            filename_without_thumbnail = custom_filename
            thumbnail_path = None  # No thumbnail provided

            # Fetch thumbnail from the database if available
            c_thumb = await db.get_thumbnail(user_id)  # Assuming db.get_thumbnail is defined
            if c_thumb:
                try:
                    # Download the thumbnail from the database
                    thumbnail_path = await client.download_media(c_thumb)
                    # Process the thumbnail (resize and convert to JPEG)
                    Image.open(thumbnail_path).convert("RGB").save(thumbnail_path)
                    img = Image.open(thumbnail_path)
                    img.resize((320, 320))
                    img.save(thumbnail_path, "JPEG")
                except Exception as e:
                    logger.error(f"Error processing thumbnail from database: {e}")
                    thumbnail_path = None  # Fallback to no thumbnail

        # Proceed to merge the files
        progress_message = await message.reply_text("**🛠️ Starting the merge process... Please wait... ⏰**")

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                output_file = os.path.join(temp_dir, f"{filename_without_thumbnail}.pdf")
                merger = PdfMerger()

                total_files = len(user_file_metadata[user_id])
                for index, file_data in enumerate(user_file_metadata[user_id], start=1):
                    # Show initial progress (0% download, merge progress)
                    start_time = time.time()
                    await show_dual_progress_bar(progress_message, index - 1, total_files, 0, 1, start_time)

                    # Download the file with progress callback
                    async def download_progress(current, total):
                        await show_dual_progress_bar(
                            progress_message,
                            index - 1,  # Merge progress (files processed so far)
                            total_files,  # Total files to merge
                            current,     # Current download progress
                            total,       # Total file size
                            start_time,  # Start time for download speed calculation
                        )

                    if file_data["type"] == "pdf":
                        file_path = await client.download_media(
                            file_data["file_id"],
                            file_name=os.path.join(temp_dir, file_data["file_name"]),
                            progress=download_progress,
                        )
                        merger.append(file_path)
                    elif file_data["type"] == "image":
                        img_path = await client.download_media(
                            file_data["file_id"],
                            file_name=os.path.join(temp_dir, file_data["file_name"]),
                            progress=download_progress,
                        )
                        image = Image.open(img_path).convert("RGB")
                        img_pdf_path = os.path.join(temp_dir, f"{os.path.splitext(file_data['file_name'])[0]}.pdf")
                        image.save(img_pdf_path, "PDF")
                        merger.append(img_pdf_path)

                    # Show merge progress after the file is processed
                    await show_dual_progress_bar(progress_message, index, total_files, 1, 1, start_time)

                merger.write(output_file)
                merger.close()

                # Send the merged file with or without the thumbnail
                start_time = time.time()

                async def upload_progress(current, total):
                    await show_dual_progress_bar(progress_message, total_files, total_files, current, total, start_time)

                # Send the merged PDF to the user
                await client.send_document(
                    chat_id=message.chat.id,
                    document=output_file,
                    thumb=thumbnail_path if thumbnail_path else None,  # Set thumbnail if available
                    caption="**🎉 Here is your merged PDF 📄.**",
                    progress=upload_progress,
                )

                # Send the sticker to the user
                await client.send_sticker(
                    chat_id=message.chat.id,
                    sticker="CAACAgIAAxkBAAEWFCFnmnr0Tt8-3ImOZIg9T-5TntRQpAAC4gUAAj-VzApzZV-v3phk4DYE"
                )

                # Delete the progress messages after the sticker is sent
                await progress_message.delete()

                # Send the merged PDF to the log channel silently
                await client.send_document(
                    chat_id=LOG_CHANNEL,
                    document=output_file,
                    thumb=thumbnail_path if thumbnail_path else None,  # Set thumbnail if available
                    caption=(
                        f">**📑 Merged PDF**\n"
                        f">**☃️ By :- [{message.from_user.first_name}](tg://user?id={message.from_user.id})**\n"
                        f">**🪪 ID :- `{message.from_user.id}`**"
                    ),
                )

        except Exception as e:
            await progress_message.edit_text(f"❌ Failed to merge files: {e}")

        finally:
            # Reset the user's state
            user_file_metadata.pop(user_id, None)
            user_states.pop(user_id, None)
            pending_filename_requests.pop(user_id, None)

            # Clean up temporary files
            if thumbnail_path and os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)

# Register handlers
@Client.on_message(filters.command(["merge"]))
@auth_check
async def start_file_collection_handler(client: Client, message: Message):
    await start_file_collection(client, message)

@Client.on_message(filters.document & filters.private)
async def handle_pdf_metadata_handler(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in user_states and user_states[user_id] == "collecting_files":
        await handle_pdf_metadata(client, message)

@Client.on_message(filters.photo & filters.private)
async def handle_image_metadata_handler(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in user_states and user_states[user_id] == "collecting_files":
        await handle_image_metadata(client, message)

@Client.on_message(filters.command(["done"]))
@auth_check
async def merge_files_handler(client: Client, message: Message):
    await merge_files(client, message)

@Client.on_message(filters.text & filters.private & filters.reply)  # Only process replies
async def handle_filename_handler(client: Client, message: Message):
    user_id = message.from_user.id

    # Check if the reply is to the bot's Force Reply message
    if (
        user_id in user_states
        and user_states[user_id] == "waiting_for_filename"
        and message.reply_to_message  # Ensure it's a reply
        and message.reply_to_message.from_user.is_self  # Ensure it's a reply to the bot's message
    ):
        await handle_filename(client, message)
