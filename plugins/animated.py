from pyrogram import Client, filters
from pyrogram.enums import ParseMode

@Client.on_message(filters.command("emoji"))
async def send_animated_emoji(client, message):
    text_with_emoji = (
        "Hello! This is an **animated emoji**: "
        "<emoji id=5472055112702629499>🔥</emoji>"
    )
    
    await client.send_message(
        chat_id=message.chat.id,
        text=text_with_emoji,
        parse_mode=ParseMode.HTML
    )
