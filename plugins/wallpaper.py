import random
import requests
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from config import LOG_CHANNEL

GITHUB_API_URL = "https://api.github.com/repos/Ur-amit-01/minimalistic-wallpaper-collection/contents/images"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/Ur-amit-01/minimalistic-wallpaper-collection/main/images/"

# Cache wallpaper list to avoid hitting GitHub rate limits
WALLPAPER_CACHE = []

def get_wallpaper_list():
    global WALLPAPER_CACHE
    if WALLPAPER_CACHE:  # Return cached list if available
        return WALLPAPER_CACHE
    try:
        response = requests.get(GITHUB_API_URL)
        if response.status_code == 200:
            files = response.json()
            WALLPAPER_CACHE = [file["name"] for file in files if file["name"].lower().endswith((".jpg", ".png"))]
            return WALLPAPER_CACHE
        else:
            print("Failed to fetch wallpapers:", response.text)
            return []
    except Exception as e:
        print("Error:", e)
        return []

def get_random_wallpaper():
    wallpapers = get_wallpaper_list()
    if not wallpapers:
        return None
    filename = random.choice(wallpapers)
    return f"{GITHUB_RAW_URL}{filename}"

@Client.on_message(filters.command("wallpaper") & filters.channel)
async def send_wallpaper(client, message):
    image_url = get_random_wallpaper()
    if not image_url:
        await message.reply_text("⚠️ No wallpapers found. Check the repository.")
        return
    
    timestamp = datetime.now().strftime("[%H:%M:%S] [%d-%m_%Y]")  # Get the current time
    
    await message.reply_photo(
        photo=image_url,
        caption=f"**🖼️ ʜᴇʀᴇ'ꜱ ᴀ ᴍɪɴɪᴍᴀʟɪꜱᴛɪᴄ ᴡᴀʟʟᴘᴀᴘᴇʀ!**\n\n⏰ **ʟᴀꜱᴛ ʀᴇꜰʀᴇꜱʜᴇᴅ: {timestamp}**",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 ɢᴇɴᴇʀᴀᴛᴇ ɴᴇᴡ ᴡᴀʟʟᴘᴀᴘᴇʀ", callback_data="refresh_wallpaper")]
        ])
    )

@Client.on_callback_query(filters.regex("refresh_wallpaper"))
async def refresh_wallpaper(client: Client, query: CallbackQuery):
    await query.answer()  # Acknowledge button press
    
    new_image_url = get_random_wallpaper()
    if not new_image_url:
        await query.message.reply_text("⚠️ No wallpapers available.")
        return
    
    timestamp = datetime.now().strftime("[%H:%M:%S] [%d-%m_%Y]")  # Get current time
    user = query.from_user  # Get user details
    
    try:
        # Edit the main message to update the wallpaper and timestamp
        await query.message.edit_media(
            media=InputMediaPhoto(new_image_url),
            caption=f"**🖼️ ʜᴇʀᴇ'ꜱ ᴀ ᴍɪɴɪᴍᴀʟɪꜱᴛɪᴄ ᴡᴀʟʟᴘᴀᴘᴇʀ!**\n\n⏰ **ʟᴀꜱᴛ ʀᴇꜰʀᴇꜱʜᴇᴅ: {timestamp}**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 ɢᴇɴᴇʀᴀᴛᴇ ɴᴇᴡ ᴡᴀʟʟᴘᴀᴘᴇʀ", callback_data="refresh_wallpaper")]
            ])
        )

        # Send log message to Log Channel
        log_message = f"""
🖼️ **Wallpaper Refreshed**
👤 **User:** [{user.first_name}](tg://user?id={user.id})
🆔 **User ID:** `{user.id}`
🕒 **Timestamp:** `{timestamp}`
"""
        await client.send_message(LOG_CHANNEL, log_message)

    except Exception as e:
        await query.message.reply_text(f"⚠️ Error: {str(e)}")
