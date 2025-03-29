from pyrogram import Client, filters

CUSTOM_EMOJI_ID = "5472055112702629499"  # Your premium emoji ID

@Client.on_message(filters.command("emoji"))
def send_premium_emoji(client, message):
    client.send_message(
        chat_id=message.chat.id,
        text=f"<emoji id='{CUSTOM_EMOJI_ID}'></emoji> Here is your premium emoji!",
        parse_mode="html"
    )
