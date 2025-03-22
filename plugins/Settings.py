from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from helper.database import db
from config import RENAME_MODE
import asyncio
from plugins.start import *

@Client.on_message(filters.private & filters.command("settings"))
async def open_settings(client, message):
    if RENAME_MODE == False:
        return

    user_id = message.from_user.id
    await update_settings_message(client, message, user_id, new_message=True)

@Client.on_callback_query(filters.regex("^settings$"))
async def callback_settings(client, query):
    if RENAME_MODE == False:
        return

    user_id = query.from_user.id
    await update_settings_message(client, query.message, user_id)

@Client.on_callback_query(filters.regex("toggle_thumb"))
async def toggle_thumb(client, query: CallbackQuery):
    if RENAME_MODE == False:
        return

    user_id = query.from_user.id

    # Send the prompt message and wait for the user's response
    prompt_msg = await client.send_message(user_id, "**Send me your thumbnail**")
    thumb_msg = await client.listen(user_id)  # Wait for the user to send a thumbnail
    if thumb_msg.photo:
        await db.set_thumbnail(user_id, file_id=thumb_msg.photo.file_id)
        await thumb_msg.delete()  # Delete the received thumbnail message
        await prompt_msg.delete()  # Delete the prompt message

    await update_settings_message(client, query.message, user_id)

@Client.on_callback_query(filters.regex("toggle_caption"))
async def toggle_caption(client, query: CallbackQuery):
    if RENAME_MODE == False:
        return

    user_id = query.from_user.id
    caption = await db.get_caption(user_id)

    # Send the prompt message and wait for the user's response
    prompt_msg = await client.send_message(user_id, "**Give me a caption to set.**\n\nAvailable Fillings:\n📂 `{filename}`\n💾 `{filesize}`\n⏰ `{duration}`")
    caption_msg = await client.listen(user_id)  # Wait for the user to send a caption
    await db.set_caption(user_id, caption=caption_msg.text)
    await caption_msg.delete()  # Delete the received caption message
    await prompt_msg.delete()  # Delete the prompt message

    await update_settings_message(client, query.message, user_id)

@Client.on_callback_query(filters.regex("view_thumb"))
async def view_thumb(client, query: CallbackQuery):
    if RENAME_MODE == False:
        return

    user_id = query.from_user.id
    thumb = await db.get_thumbnail(user_id)

    if thumb:
        sent_message = await client.send_photo(chat_id=user_id, photo=thumb)
        await asyncio.sleep(10)  # Wait for 10 seconds
        await sent_message.delete()  # Delete the sent thumbnail after 10 seconds
    else:
        await query.answer("**❌ No thumbnail found! ❌**", show_alert=True)

@Client.on_callback_query(filters.regex("see_caption"))
async def see_caption(client, query: CallbackQuery):
    if RENAME_MODE == False:
        return

    user_id = query.from_user.id
    caption = await db.get_caption(user_id)

    if caption:
        sent_message = await query.message.reply_text(f"**Your Caption:**\n\n`{caption}`")
        await asyncio.sleep(10)  # Wait for 10 seconds
        await sent_message.delete()  # Delete the sent caption after 10 seconds
    else:
        await query.answer("**❌ No caption found! ❌**", show_alert=True)

@Client.on_callback_query(filters.regex("delete_thumb"))
async def delete_thumb(client, query: CallbackQuery):
    if RENAME_MODE == False:
        return

    user_id = query.from_user.id
    thumb = await db.get_thumbnail(user_id)

    if thumb:
        await db.set_thumbnail(user_id, file_id=None)  # Delete thumbnail
        await update_settings_message(client, query.message, user_id)  # Update UI silently
    else:
        await query.answer("**❌ No thumbnail found! ❌**", show_alert=True)

@Client.on_callback_query(filters.regex("delete_caption"))
async def delete_caption(client, query: CallbackQuery):
    if RENAME_MODE == False:
        return

    user_id = query.from_user.id
    caption = await db.get_caption(user_id)

    if caption:
        await db.set_caption(user_id, caption=None)  # Delete caption
        await update_settings_message(client, query.message, user_id)  # Update UI silently
    else:
        await query.answer("**❌ No caption found! ❌**", show_alert=True)

@Client.on_callback_query(filters.regex("close"))
async def close_settings(client, query: CallbackQuery):
    await query.message.delete()

async def update_settings_message(client, message, user_id, new_message=False):
    """ Updates or sends the settings message dynamically. """
    thumb = await db.get_thumbnail(user_id)
    caption = await db.get_caption(user_id)

    thumb_status = "✅" if thumb else "❌"
    caption_status = "✅" if caption else "❌"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🖼 Thumbnail: {thumb_status}", callback_data="toggle_thumb")],
        [InlineKeyboardButton("👀 See thumb", callback_data="view_thumb"),
         InlineKeyboardButton("🗑 Delete", callback_data="delete_thumb")],
        [InlineKeyboardButton(f"📝 Caption: {caption_status}", callback_data="toggle_caption")],
        [InlineKeyboardButton("👀 See Caption", callback_data="see_caption"),
         InlineKeyboardButton("🗑 Delete", callback_data="delete_caption")],
        [InlineKeyboardButton("🏠 Home", callback_data="start")]
    ])

    text = (
        "**╭────[ꜱᴇᴛᴛɪɴɢꜱ]────〄**\n"
        "**│⋗ ꜰᴏʀ ᴍᴇʀɢᴇᴅ ᴏʀ ʀᴇɴᴀᴍᴇᴅ ꜰɪʟᴇꜱ**\n"
        "**│**\n"
        f"**│• ᴛʜᴜᴍʙ sᴛᴀᴛᴜs : {thumb_status}**\n"
        f"**│• ᴄᴀᴘᴛɪᴏɴ ᴍᴏᴅᴇ : {caption_status}**\n"
        "**╰─────────────⍟**"
    )

    if new_message:
        await message.reply_text(text, reply_markup=keyboard)
    else:
        await message.edit_text(text, reply_markup=keyboard)

@Client.on_message(filters.private & filters.command(['set_thumb']))
async def addthumbs(client, message):
    if RENAME_MODE == False:
        return 
    prompt_msg = await client.send_message(message.chat.id, "**Send me your thumbnail**")
    thumb_msg = await client.listen(message.chat.id)  # Wait for the user to send a thumbnail
    if thumb_msg.media and thumb_msg.media == enums.MessageMediaType.PHOTO:
        await db.set_thumbnail(message.from_user.id, file_id=thumb_msg.photo.file_id)
        await thumb_msg.delete()  # Delete the received thumbnail message
        await prompt_msg.delete()  # Delete the prompt message
        await message.reply("**Thumbnail saved successfully ✅️**")
    else:
        await message.reply("**This is not a picture**")

