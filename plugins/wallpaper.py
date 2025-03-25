import random
import requests
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery


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
@Client.on_message(filters.command("wallpaper") & filters.channel)
async def send_wallpaper(client, message):
    image_url = get_random_wallpaper()
    if not image_url:
        await message.reply_text("⚠️ No wallpapers found. Please check the repository.")
        return
    
    await message.reply_photo(
        photo=image_url,
        caption="Here is a minimalistic wallpaper! Click refresh for a new one.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_wallpaper")]
        ])
    )

# Callback function to refresh the wallpaper
@Client.on_callback_query(filters.regex("refresh_wallpaper"))
async def refresh_wallpaper(client: Client, query: CallbackQuery):
    new_image_url = get_random_wallpaper()
    if not new_image_url:
        await query.answer("⚠️ No new wallpapers found.", show_alert=True)
        return
    
    await query.message.edit_media(
        media=new_image_url,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_wallpaper")]
        ])
    )

