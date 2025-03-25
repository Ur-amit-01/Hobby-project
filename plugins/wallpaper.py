import random
import requests
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from datetime import datetime
from config import LOG_CHANNEL

# GitHub API URL to fetch file list from the images folder
GITHUB_API_URL = "https://api.github.com/repos/Ur-amit-01/minimalistic-wallpaper-collection/contents/images"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/Ur-amit-01/minimalistic-wallpaper-collection/main/images/"  

# Function to get the list of image filenames dynamically
def get_wallpaper_list():
    try:
        response = requests.get(GITHUB_API_URL)
        if response.status_code == 200:
            files = response.json()
            return [file["name"] for file in files if file["name"].endswith((".jpg", ".png"))]
        else:
            print("Failed to fetch file list:", response.text)
            return []
    except Exception as e:
        print("Error fetching wallpapers:", str(e))
        return []

# Function to get a random wallpaper URL
def get_random_wallpaper():
    wallpapers = get_wallpaper_list()
    if not wallpapers:
        return None
    filename = random.choice(wallpapers)
    return f"{GITHUB_RAW_URL}{filename}"

# Command to send a wallpaper in a channel
@Client.on_message(filters.command("amit") & filters.channel)
async def send_wallpaper(client, message):
    image_url = get_random_wallpaper()
    if not image_url:
        await message.reply_text("⚠️ No wallpapers found. Please check the repository.")
        return
    
    await message.reply_photo(
        photo=image_url,
        caption="✨ Minimalist Vibes! 🔥\nTap **Refresh** for more!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_wallpaper")]
        ])
    )

@Client.on_callback_query(filters.regex("refresh_wallpaper"))
async def refresh_wallpaper(client: Client, query: CallbackQuery):
    new_image_url = get_random_wallpaper()
    if not new_image_url:
        await query.answer("⚠️ No new wallpapers found.", show_alert=True)
        return

    last_updated = datetime.now().strftime("%I:%M %p || %d %B ")  # Format: 25 March 2025 | 02:30 PM

    await query.message.edit_media(
        media=InputMediaPhoto(
            media=new_image_url, 
            caption=f"> **✨ ʜᴇʀᴇ'ꜱ ᴀ ᴍɪɴɪᴍᴀʟɪꜱᴛɪᴄ ᴡᴀʟʟᴘᴀᴘᴇʀ! **\n> 🕒 **ʟᴀꜱᴛ ᴜᴘᴅᴀᴛᴇᴅ : {last_updated}**"
        ),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 ɢᴇɴᴇʀᴀᴛᴇ ɴᴇᴡ ᴡᴀʟʟᴘᴀᴘᴇʀ", callback_data="refresh_wallpaper")]
        ])
    )

    # Log the action in the LOG_CHANNEL
    user = query.from_user
    log_text = (
        f"> 📢 **Wallpaper Refreshed!**\n"
        f"👤 **User: [{user.first_name}](tg://user?id={user.id})**\n"
        f"👤 **User id:** `{user.id}`\n"
        f"🖼 **New Wallpaper: [View Image]({new_image_url})**"
    )
    await client.send_message(LOG_CHANNEL, log_text, disable_web_page_preview=True)
    await client.send_sticker(
                    chat_id=LOG_CHANNEL,
                    sticker="CAACAgUAAxkBAAIDCmfiQnY5Ue_tYOezQEoXNlU0ZvV4AAIzAQACmPYGEc09e5ZAcRZ3HgQ"
    )
