
from pyrogram import Client, filters
from pyrogram.types import MessageEntity

@Client.on_message(filters.command("wave"))
def send_animated_emoji(client, message):
    client.send_message(
        chat_id=message.chat.id,
        text="Hey 👋",  # Text with emoji placeholder
        entities=[
            MessageEntity(
                type="custom_emoji",
                offset=4,  # Position of emoji in text
                length=2,  # Length of emoji (1-2 chars)
                custom_emoji_id=5472055112702629499  # Replace with actual emoji ID
            )
        ]
    )
