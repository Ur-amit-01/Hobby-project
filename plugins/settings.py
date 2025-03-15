from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from helper.database import db
from config import RENAME_MODE

# ======================= Settings Command Handler ======================= #
@Client.on_message(filters.command("settings") & filters.private)
async def settings_command_handler(client: Client, message: Message):
    if RENAME_MODE == False:
        return await message.reply_text("❌ **Rename mode is disabled. Settings are unavailable.**")

    # Create buttons for settings
    buttons = [
        [
            InlineKeyboardButton("🖼️ Set Thumbnail", callback_data="set_thumb"),
            InlineKeyboardButton("👀 Show Thumbnail", callback_data="show_thumb"),
            InlineKeyboardButton("🗑️ Delete Thumbnail", callback_data="del_thumb"),
        ],
        [
            InlineKeyboardButton("📝 Set Caption", callback_data="set_caption"),
            InlineKeyboardButton("👀 Show Caption", callback_data="show_caption"),
            InlineKeyboardButton("🗑️ Delete Caption", callback_data="del_caption"),
        ],
        [InlineKeyboardButton("🔙 Back", callback_data="start")],
    ]

    # Send the settings menu
    await message.reply_text(
        "**⚙️ Settings Menu**\n\n"
        "Here you can manage your thumbnail and caption settings.",
        reply_markup=InlineKeyboardMarkup(buttons),
    )

# ======================= Set Thumbnail Callback Handler ======================= #
@Client.on_callback_query(filters.regex("^set_thumb$"))
async def set_thumbnail_callback_handler(client: Client, query: CallbackQuery):
    if RENAME_MODE == False:
        return await query.answer("❌ Rename mode is disabled. Settings are unavailable.", show_alert=True)

    # Ask the user to send a photo
    await query.message.edit_text(
        "**🖼️ Send me your thumbnail.**\n\n"
        "⚠️ The photo will be resized to 320x320 pixels.",
    )
    user_states[query.from_user.id] = "waiting_for_thumbnail"  # Set user state

# ======================= Show Thumbnail Callback Handler ======================= #
@Client.on_callback_query(filters.regex("^show_thumb$"))
async def show_thumbnail_callback_handler(client: Client, query: CallbackQuery):
    if RENAME_MODE == False:
        return await query.answer("❌ Rename mode is disabled. Settings are unavailable.", show_alert=True)

    # Fetch the thumbnail from the database
    thumb = await db.get_thumbnail(query.from_user.id)
    if thumb:
        await client.send_photo(
            chat_id=query.message.chat.id,
            photo=thumb,
            caption="**🖼️ Your current thumbnail:**",
        )
    else:
        await query.answer("😔 Sorry! No thumbnail found...", show_alert=True)

# ======================= Delete Thumbnail Callback Handler ======================= #
@Client.on_callback_query(filters.regex("^del_thumb$"))
async def delete_thumbnail_callback_handler(client: Client, query: CallbackQuery):
    if RENAME_MODE == False:
        return await query.answer("❌ Rename mode is disabled. Settings are unavailable.", show_alert=True)

    # Delete the thumbnail from the database
    await db.set_thumbnail(query.from_user.id, file_id=None)
    await query.answer("✅ Thumbnail deleted successfully!", show_alert=True)

# ======================= Set Caption Callback Handler ======================= #
@Client.on_callback_query(filters.regex("^set_caption$"))
async def set_caption_callback_handler(client: Client, query: CallbackQuery):
    if RENAME_MODE == False:
        return await query.answer("❌ Rename mode is disabled. Settings are unavailable.", show_alert=True)

    # Ask the user to send a caption
    await query.message.edit_text(
        "**📝 Send your custom caption.**\n\n"
        "You can use the following placeholders:\n"
        "- `{filename}`: File name\n"
        "- `{filesize}`: File size\n"
        "- `{duration}`: Duration (for media files)",
    )
    user_states[query.from_user.id] = "waiting_for_caption"  # Set user state

# ======================= Show Caption Callback Handler ======================= #
@Client.on_callback_query(filters.regex("^show_caption$"))
async def show_caption_callback_handler(client: Client, query: CallbackQuery):
    if RENAME_MODE == False:
        return await query.answer("❌ Rename mode is disabled. Settings are unavailable.", show_alert=True)

    # Fetch the caption from the database
    caption = await db.get_caption(query.from_user.id)
    if caption:
        await query.message.edit_text(
            f"**📝 Your current caption:**\n\n`{caption}`",
        )
    else:
        await query.answer("😔 Sorry! No caption found...", show_alert=True)

# ======================= Delete Caption Callback Handler ======================= #
@Client.on_callback_query(filters.regex("^del_caption$"))
async def delete_caption_callback_handler(client: Client, query: CallbackQuery):
    if RENAME_MODE == False:
        return await query.answer("❌ Rename mode is disabled. Settings are unavailable.", show_alert=True)

    # Delete the caption from the database
    await db.set_caption(query.from_user.id, caption=None)
    await query.answer("✅ Caption deleted successfully!", show_alert=True)

# ======================= Handle Thumbnail Input ======================= #
@Client.on_message(filters.photo & filters.private)
async def handle_thumbnail_input(client: Client, message: Message):
    user_id = message.from_user.id

    # Check if the user is in the "waiting_for_thumbnail" state
    if user_id in user_states and user_states[user_id] == "waiting_for_thumbnail":
        # Set the thumbnail in the database
        await db.set_thumbnail(user_id, message.photo.file_id)
        await message.reply_text("✅ Thumbnail saved successfully!")
        user_states.pop(user_id, None)  # Reset user state

# ======================= Handle Caption Input ======================= #
@Client.on_message(filters.text & filters.private)
async def handle_caption_input(client: Client, message: Message):
    user_id = message.from_user.id

    # Check if the user is in the "waiting_for_caption" state
    if user_id in user_states and user_states[user_id] == "waiting_for_caption":
        # Set the caption in the database
        await db.set_caption(user_id, caption=message.text)
        await message.reply_text("✅ Caption saved successfully!")
        user_states.pop(user_id, None)  # Reset user state

