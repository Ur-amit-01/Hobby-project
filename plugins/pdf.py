import requests
import os
import re
import logging
import tempfile
import asyncio
import time
from PIL import Image
from pyrogram import Client, filters
from PyPDF2 import PdfMerger
from pyrogram.types import Message
from config import LOG_CHANNEL

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

class MergePlugin:
    def __init__(self):
        self.pending_filename_requests = {}
        self.user_file_metadata = {}  # Store metadata for each user's files
        self.user_states = {}  # Track user states

    async def reset_user_state(self, user_id: int):
        await asyncio.sleep(120)  # 2 minutes
        if user_id in self.user_file_metadata:
            self.user_file_metadata.pop(user_id, None)
            self.pending_filename_requests.pop(user_id, None)
            self.user_states.pop(user_id, None)
            logger.info(f"Reset state for user {user_id} due to inactivity.")

    async def show_download_progress(self, current, total, progress_message, start_time):
        elapsed_time = time.time() - start_time
        speed = current / elapsed_time if elapsed_time > 0 else 0  # in bytes per second
        speed_mb = speed / (1024 * 1024)  # Convert to MB/s

        progress = min(current / total, 1.0)  # Ensure progress doesn't exceed 1.0
        percentage = int(progress * 100)

        # Calculate remaining time
        remaining_bytes = total - current
        remaining_time = remaining_bytes / speed if speed > 0 else 0

        # Format the progress message
        progress_text = (
            f"╭━━━━❰ File Is Downloading... ❱━➣\n"
            f"┣⪼ 🗂️ : {current / (1024 * 1024):.2f} MB | {total / (1024 * 1024):.2f} MB\n"
            f"┣⪼ ⏳️ : {percentage}%\n"
            f"┣⪼ 🚀 : {speed_mb:.2f} MB/s\n"
            f"┣⪼ ⏱️ : {int(remaining_time)}s\n"
            f"╰━━━━━━━━━━━━━━━➣"
        )
        await progress_message.edit_text(progress_text)

    async def show_merge_progress(self, progress_message, current, total):
        progress = min(current / total, 1.0)  # Ensure progress doesn't exceed 1.0
        filled_length = int(10 * progress)
        bar = "●" * filled_length + "○" * (10 - filled_length)  # Filled and empty parts
        percentage = int(progress * 100)
        text = f"**🛠️ Merging Files...**\n`[{bar}]` {percentage}% ({current}/{total})"
        await progress_message.edit_text(text)

    async def show_upload_progress(self, current, total, progress_message, start_time):
        elapsed_time = time.time() - start_time
        speed = current / elapsed_time if elapsed_time > 0 else 0  # in bytes per second
        speed_mb = speed / (1024 * 1024)  # Convert to MB/s

        progress = min(current / total, 1.0)  # Ensure progress doesn't exceed 1.0
        percentage = int(progress * 100)

        # Calculate remaining time
        remaining_bytes = total - current
        remaining_time = remaining_bytes / speed if speed > 0 else 0

        # Format the progress message
        progress_text = (
            f"╭━━━━❰ File Is Uploading... ❱━➣\n"
            f"┣⪼ 🗂️ : {current / (1024 * 1024):.2f} MB | {total / (1024 * 1024):.2f} MB\n"
            f"┣⪼ ⏳️ : {percentage}%\n"
            f"┣⪼ 🚀 : {speed_mb:.2f} MB/s\n"
            f"┣⪼ ⏱️ : {int(remaining_time)}s\n"
            f"╰━━━━━━━━━━━━━━━➣"
        )
        await progress_message.edit_text(progress_text)

    async def start_file_collection(self, client: Client, message: Message):
        user_id = message.from_user.id
        self.user_file_metadata[user_id] = []  # Reset file list for the user
        self.user_states[user_id] = "collecting_files"  # Set user state
        await message.reply_text(
            "**📤 Uᴘʟᴏᴀᴅ ʏᴏᴜʀ ғɪʟᴇs ɪɴ sᴇǫᴜᴇɴᴄᴇ, ᴛʏᴘᴇ /done ✅, ᴀɴᴅ ɢᴇᴛ ʏᴏᴜʀ ᴍᴇʀɢᴇᴅ PDF !! 🧾**"
        )
        # Start a timer to reset the state after 2 minutes
        asyncio.create_task(self.reset_user_state(user_id))

    async def handle_pdf_metadata(self, client: Client, message: Message):
        user_id = message.from_user.id

        # Only accept PDFs if the user has started the merge process
        if user_id not in self.user_states or self.user_states[user_id] != "collecting_files":
            return

        if message.document.mime_type != "application/pdf":
            await message.reply_text("❌ This is not a valid PDF file. Please send a PDF 📑.")
            return

        if len(self.user_file_metadata[user_id]) >= 20:
            await message.reply_text("⚠️ You can upload up to 20 files. Type /done ✅ to merge them.")
            return

        if message.document.file_size > MAX_FILE_SIZE:
            await message.reply_text("🚫 File size is too large! Please send a file under 500MB.")
            return

        self.user_file_metadata[user_id].append(
            {
                "type": "pdf",
                "file_id": message.document.file_id,
                "file_name": message.document.file_name,
            }
        )
        await message.reply_text(
            f"**➕ PDF ᴀᴅᴅᴇᴅ ᴛᴏ ᴛʜᴇ ʟɪsᴛ! 📄 ({len(self.user_file_metadata[user_id])} files added so far.)**\n"
            "**Sᴇɴᴅ ᴍᴏʀᴇ ғɪʟᴇs ᴏʀ ᴜsᴇ /done ✅ ᴛᴏ ᴍᴇʀɢᴇ ᴛʜᴇᴍ.**"
        )

    async def handle_image_metadata(self, client: Client, message: Message):
        user_id = message.from_user.id

        # Only accept images if the user has started the merge process
        if user_id not in self.user_states or self.user_states[user_id] != "collecting_files":
            return

        self.user_file_metadata[user_id].append(
            {
                "type": "image",
                "file_id": message.photo.file_id,
                "file_name": f"photo_{len(self.user_file_metadata[user_id]) + 1}.jpg",
            }
        )
        await message.reply_text(
            f"➕ Image added to the list! 🖼️ ({len(self.user_file_metadata[user_id])} files added so far.)\n"
            "Send more files or use /done ✅ to merge them."
        )

    async def merge_files(self, client: Client, message: Message):
        user_id = message.from_user.id

        if user_id not in self.user_file_metadata or not self.user_file_metadata[user_id]:
            await message.reply_text("**⚠️ Yᴏᴜ ʜᴀᴠᴇɴ'ᴛ ᴀᴅᴅᴇᴅ ᴀɴʏ ғɪʟᴇs ʏᴇᴛ. Usᴇ /merge ᴛᴏ sᴛᴀʀᴛ.**")
            return

        await message.reply_text("**✍️ Type a name for your merged PDF 📄.**")
        self.user_states[user_id] = "waiting_for_filename"  # Set user state

    async def handle_filename(self, client: Client, message: Message):
        user_id = message.from_user.id

        # Only process if the user is in the "waiting_for_filename" state
        if user_id not in self.user_states or self.user_states[user_id] != "waiting_for_filename":
            return

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

            except Exception as e:
                await message.reply_text(f"❌ Error while downloading the thumbnail: {e}")
                return

        else:
            filename_without_thumbnail = custom_filename
            thumbnail_path = None  # No thumbnail provided

        # Proceed to merge the files
        progress_message = await message.reply_text("**🛠️ Merging your files... Please wait... ⏰**")

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                output_file = os.path.join(temp_dir, f"{filename_without_thumbnail}.pdf")
                merger = PdfMerger()

                total_files = len(self.user_file_metadata[user_id])
                for index, file_data in enumerate(self.user_file_metadata[user_id], start=1):
                    if file_data["type"] == "pdf":
                        start_time = time.time()
                        file_path = await client.download_media(
                            file_data["file_id"],
                            file_name=os.path.join(temp_dir, file_data["file_name"]),
                            progress=lambda current, total: asyncio.create_task(
                                self.show_download_progress(current, total, progress_message, start_time)
                        )
                        merger.append(file_path)
                        await self.show_merge_progress(progress_message, index, total_files)
                    elif file_data["type"] == "image":
                        start_time = time.time()
                        img_path = await client.download_media(
                            file_data["file_id"],
                            file_name=os.path.join(temp_dir, file_data["file_name"]),
                            progress=lambda current, total: asyncio.create_task(
                                self.show_download_progress(current, total, progress_message, start_time)
                        )
                        image = Image.open(img_path).convert("RGB")
                        img_pdf_path = os.path.join(temp_dir, f"{os.path.splitext(file_data['file_name'])[0]}.pdf")
                        image.save(img_pdf_path, "PDF")
                        merger.append(img_pdf_path)
                        await self.show_merge_progress(progress_message, index, total_files)

                merger.write(output_file)
                merger.close()

                # Send the merged file with or without the thumbnail
                start_time = time.time()
                if thumbnail_path:
                    # Send to user
                    await client.send_document(
                        chat_id=message.chat.id,
                        document=output_file,
                        thumb=thumbnail_path,  # Set the thumbnail
                        caption="**🎉 Here is your merged PDF 📄.**",
                        progress=lambda current, total: asyncio.create_task(
                            self.show_upload_progress(current, total, progress_message, start_time)
                        )
                    )
                    # Send to log channel
                    await client.send_document(
                        chat_id=LOG_CHANNEL,
                        document=output_file,
                        thumb=thumbnail_path,
                        caption=f"**📑 Merged PDF from [{message.from_user.first_name}](tg://user?id={message.from_user.id}\n@z900_Robot**)",
                        progress=lambda current, total: asyncio.create_task(
                            self.show_upload_progress(current, total, progress_message, start_time)
                        )
                    )
                else:
                    # Send to user
                    await client.send_document(
                        chat_id=message.chat.id,
                        document=output_file,
                        caption="**🎉 Here is your merged PDF 📄.**",
                        progress=lambda current, total: asyncio.create_task(
                            self.show_upload_progress(current, total, progress_message, start_time)
                        )
                    )
                    # Send to log channel
                    await client.send_document(
                        chat_id=LOG_CHANNEL,
                        document=output_file,
                        caption=f"**📑 Merged PDF from [{message.from_user.first_name}](tg://user?id={message.from_user.id}\n@z900_Robot**)",
                        progress=lambda current, total: asyncio.create_task(
                            self.show_upload_progress(current, total, progress_message, start_time)
                        )
                    )
                await progress_message.delete()

                # Send a sticker after sending the merged PDF
                await client.send_sticker(
                    chat_id=message.chat.id,
                    sticker="CAACAgIAAxkBAAEWFCFnmnr0Tt8-3ImOZIg9T-5TntRQpAAC4gUAAj-VzApzZV-v3phk4DYE"  # Replace with your preferred sticker ID
                )

        except Exception as e:
            await progress_message.edit_text(f"❌ Failed to merge files: {e}")

        finally:
            # Reset the user's state
            self.user_file_metadata.pop(user_id, None)
            self.user_states.pop(user_id, None)
            self.pending_filename_requests.pop(user_id, None)

# Initialize the plugin
merge_plugin = MergePlugin()

# Register handlers
@Client.on_message(filters.command(["merge"]))
async def start_file_collection(client: Client, message: Message):
    await merge_plugin.start_file_collection(client, message)

@Client.on_message(filters.document & filters.private)
async def handle_pdf_metadata(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in merge_plugin.user_states and merge_plugin.user_states[user_id] == "collecting_files":
        await merge_plugin.handle_pdf_metadata(client, message)

@Client.on_message(filters.photo & filters.private)
async def handle_image_metadata(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in merge_plugin.user_states and merge_plugin.user_states[user_id] == "collecting_files":
        await merge_plugin.handle_image_metadata(client, message)

@Client.on_message(filters.command(["done"]))
async def merge_files(client: Client, message: Message):
    await merge_plugin.merge_files(client, message)

@Client.on_message(filters.text & filters.private & ~filters.command(["start", "set_thumb", "del_thumb", "view_thumb", "see_caption", "del_caption", "set_caption", "rename", "cancel", "ask", "id", "set", "telegraph", "stickerid", "accept", "users", "broadcast"]) & ~filters.regex("https://t.me/"))           
async def handle_filename(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in merge_plugin.user_states and merge_plugin.user_states[user_id] == "waiting_for_filename":
        await merge_plugin.handle_filename(client, message)
        
