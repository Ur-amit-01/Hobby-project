import random
import requests
import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from datetime import datetime
from config import LOG_CHANNEL, GITHUB_TOKEN

# GitHub API Details
GITHUB_API_URL = "https://api.github.com/repos/Ur-amit-01/minimalistic-wallpaper-collection/contents/images"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/Ur-amit-01/minimalistic-wallpaper-collection/main/images/"  

HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

# Caching mechanism to avoid frequent API requests
wallpaper_cache = []
last_updated = 0  # Timestamp of last update

# Function to get the list of image filenames dynamically
def get_wallpaper_list():
    global wallpaper_cache, last_updated
    
    # If cache is fresh (less than 1 hour old), use it
    if time.time() - last_updated < 3600 and wallpaper_cache:
        return wallpaper_cache  

    try:
        response = requests.get(GITHUB_API_URL, headers=HEADERS)
        print(f"GitHub API Status: {response.status_code}")
        print(f"Headers: {response.headers}")  # Debugging API rate limit
        
        if response.status_code == 200:
            files = response.json()
            wallpaper_cache = [file["name"] for file in files if file["name"].endswith((".jpg", ".png"))]
            last_updated = time.time()
            return wallpaper_cache
        
        elif response.status_code == 403:  # Rate limit exceeded
            print("⚠️ GitHub API rate limit hit! Using cached wallpapers.")
        
        else:
            print("Failed to fetch file list:", response.text)
    
    except Exception as e:
        print("Error fetching wallpapers:", str(e))
    
    return wallpaper_cache  # Return cached data if API fails

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
    
    await query.message.edit_media(
        media=InputMediaPhoto(
            media=new_image_url, 
            caption="• **Wallpaper Generator Bot 🎨 ...**\n• **Click the button and witness the magic 🧞‍♂️...**"
        ),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Generate New Wallpaper", callback_data="refresh_wallpaper")]
        ])
    )

    # Log the action in the LOG_CHANNEL
    user = query.from_user
    log_text = (
        f"> 📢 **Wallpaper Refreshed!**\n"
        f"👤 **User: [{user.first_name}](tg://user?id={user.id})**\n"
        f"🆔 **User ID:** `{user.id}`\n"
        f"🖼 **New Wallpaper: [View Image]({new_image_url})**"
    )
    await client.send_message(LOG_CHANNEL, log_text, disable_web_page_preview=True)
    await client.send_sticker(
        chat_id=LOG_CHANNEL,
        sticker="CAACAgUAAxkBAAIDCmfiQnY5Ue_tYOezQEoXNlU0ZvV4AAIzAQACmPYGEc09e5ZAcRZ3HgQ"
    )
