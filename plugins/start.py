from asyncio import sleep
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message, BotCommand
from config import *
from helper.txt import mr
from helper.database import db
from pyrogram.errors import *
import random
from plugins.Fsub import auth_check
from plugins.Settings import back_to_settings

# =====================================================================================
@Client.on_message(filters.private & filters.command("start"))
@auth_check
async def start(client, message):
    try:
        await message.react(emoji=random.choice(REACTIONS), big=True)
    except:
        pass    
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id)
        total_users = await db.total_users_count()
        await client.send_message(LOG_CHANNEL, LOG_TEXT.format(message.from_user.mention, message.from_user.id, total_users))
    
    txt = (
        f"> **✨👋🏻 Hey {message.from_user.mention} !!**\n\n"
        f"**🔋 ɪ ᴀᴍ ᴀɴ ᴀᴅᴠᴀɴᴄᴇ ʙᴏᴛ ᴅᴇꜱɪɢɴᴇᴅ ᴛᴏ ᴀꜱꜱɪꜱᴛ ʏᴏᴜ. ɪ ᴄᴀɴ ᴍᴇʀɢᴇ ᴘᴅꜰ/ɪᴍᴀɢᴇꜱ , ʀᴇɴᴀᴍᴇ ʏᴏᴜʀ ꜰɪʟᴇꜱ ᴀɴᴅ ᴍᴜᴄʜ ᴍᴏʀᴇ.**\n\n"
        f"**🔘 ᴄʟɪᴄᴋ ᴏɴ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ ᴛᴏ ʟᴇᴀʀɴ ᴍᴏʀᴇ ᴀʙᴏᴜᴛ ᴍʏ ғᴜɴᴄᴛɪᴏɴs!**\n\n"
        f"> **ᴅᴇᴠᴇʟᴏᴘᴇʀ 🧑🏻‍💻 :- @Axa_bachha**"
    )
    button = InlineKeyboardMarkup([
        [InlineKeyboardButton('📜 ᴀʙᴏᴜᴛ', callback_data='about'), InlineKeyboardButton('🕵🏻‍♀️ ʜᴇʟᴘ', callback_data='help')],
        [InlineKeyboardButton("⚙️ ꜱᴇᴛᴛɪɴɢꜱ ", callback_data="settings")]
    ])
    if START_PIC:
        await message.reply_photo(START_PIC, caption=txt, reply_markup=button)
    else:
        await message.reply_text(text=txt, reply_markup=button, disable_web_page_preview=True)
        
# =====================================================================================

# Set bot commands
@Client.on_message(filters.command("set") & filters.user(ADMIN))
async def set_commands(client: Client, message: Message):
    await client.set_bot_commands([
        BotCommand("start", "🤖 Start the bot"),
        BotCommand("merge", "🛠 Start PDF merge"),
        BotCommand("done", "📂 Merge PDFs"),
        BotCommand("telegraph", "🌐 Get Telegraph link"),
        BotCommand("stickerid", "🎭 Get sticker ID"),
        BotCommand("accept", "✅ Accept pending join requests"),
        BotCommand("users", "👥 Total users"),
        BotCommand("broadcast", "📢 Send message")
    ])
    await message.reply_text("✅ Bot commands have been set.")

# ========================================= CALLBACKS =============================================
# Callback Query Handler
@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    data = query.data

    if data == "start":
        txt = (
            f"> **✨👋🏻 Hey {query.from_user.mention} !!**\n\n"
            f"**🔋 ɪ ᴀᴍ ᴀɴ ᴀᴅᴠᴀɴᴄᴇ ʙᴏᴛ ᴅᴇꜱɪɢɴᴇᴅ ᴛᴏ ᴀꜱꜱɪꜱᴛ ʏᴏᴜ. ɪ ᴄᴀɴ ᴍᴇʀɢᴇ ᴘᴅꜰ/ɪᴍᴀɢᴇꜱ , ʀᴇɴᴀᴍᴇ ʏᴏᴜʀ ꜰɪʟᴇꜱ ᴀɴᴅ ᴍᴜᴄʜ ᴍᴏʀᴇ.**\n\n"
            f"**🔘 ᴄʟɪᴄᴋ ᴏɴ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ ᴛᴏ ʟᴇᴀʀɴ ᴍᴏʀᴇ ᴀʙᴏᴜᴛ ᴍʏ ғᴜɴᴄᴛɪᴏɴs!**\n\n"
            f"> **ᴅᴇᴠᴇʟᴏᴘᴇʀ 🧑🏻‍💻 :- @Axa_bachha**"
        )
        
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton('📜 ᴀʙᴏᴜᴛ', callback_data='about'),
             InlineKeyboardButton('🕵🏻‍♀️ ʜᴇʟᴘ', callback_data='help')],
            [InlineKeyboardButton("⚙️ ꜱᴇᴛᴛɪɴɢꜱ ", callback_data="settings")]
        ])

    elif data == "help":
        txt = HELP_TXT
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("ʀᴇᴏ̨ᴜᴇsᴛ ᴀᴄᴄᴇᴘᴛᴏʀ", callback_data="request"),
             InlineKeyboardButton("ᴍᴇʀɢᴇ 📄", callback_data="merger")],
            [InlineKeyboardButton("ʀᴇsᴛʀɪᴄᴛᴇᴅ ᴄᴏɴᴛᴇɴᴛ sᴀᴠᴇʀ", callback_data="restricted")],
            [InlineKeyboardButton('ᴛᴇʟᴇɢʀᴀᴘʜ', callback_data='tele'),
             InlineKeyboardButton('ꜱᴛɪᴄᴋᴇʀ-ɪᴅ', callback_data='sticker')],
            [InlineKeyboardButton('ғɪʟᴇ ʀᴇɴᴀᴍᴇ ✍🏻📃', callback_data='rename')],
            [InlineKeyboardButton('🏠 𝙷𝙾𝙼𝙴 🏠', callback_data='start')]
        ])

    elif data == "about":
        txt = ABOUT_TXT.format(client.mention)
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🤖 ᴅᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/axa_bachha")],
            [InlineKeyboardButton("🔒 Close", callback_data="close"),
             InlineKeyboardButton("🏠 𝙷𝙾𝙼𝙴 🏠", callback_data="start")]
        ])

    elif data == "rename":
        await query.message.edit_text(
            text=Rename_TXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("◀️ 𝙱𝙰𝙲𝙺", callback_data="help")]
            ])
        )

    elif data == "close":
        try:
            await query.message.delete()
            await query.message.reply_to_message.delete()
        except:
            await query.message.delete()
        return

    elif data == "sticker":
        txt = STICKER_TXT
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ 𝙱𝙰𝙲𝙺", callback_data="help")]
        ])

    elif data == "tele":
        txt = TELEGRAPH_TXT
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ 𝙱𝙰𝙲𝙺", callback_data="help")]
        ])

    elif data == "restricted":
        txt = RESTRICTED_TXT
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ 𝙱𝙰𝙲𝙺", callback_data="help")]
        ])

    elif data == "merger":
        txt = MERGER_TXT
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ 𝙱𝙰𝙲𝙺", callback_data="help")]
        ])

    elif data == "request":
        txt = REQUEST_TXT
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ 𝙱𝙰𝙲𝙺", callback_data="help")]
        ])

    await query.message.edit_text(text=txt, reply_markup=reply_markup, disable_web_page_preview=True)


# ========================================= TEXTS =============================================

LOG_TEXT = """<blockquote><b>#NewUser ॥ @z900_Robot</b></blockquote>
<blockquote><b>☃️ Nᴀᴍᴇ :~ {}
🪪 ID :~ <code>{}</code>
👨‍👨‍👦‍👦 ᴛᴏᴛᴀʟ :~ {}</b></blockquote>"""

PROGRESS_BAR = """
╭━━━━❰ Gangster Hacking... ❱━➣
┣⪼ 🗂️ : {1} | {2}
┣⪼ ⏳️ : {0}%
┣⪼ 🚀 : {3}/s
┣⪼ ⏱️ : {4}
╰━━━━━━━━━━━━━━━➣ """

ABOUT_TXT = """
<b>╭───────────⍟
├➢ ᴍʏꜱᴇʟꜰ : {}
├➢ ᴏᴡɴᴇʀ : <a href=https://t.me/axa_bachha>𝐻𝑜𝑚𝑜 𝑠𝑎𝑝𝑖𝑒𝑛『❅』</a>
├➢ ʟɪʙʀᴀʀʏ : <a href=https://github.com/pyrogram>ᴘʏʀᴏɢʀᴀᴍ</a>
├➢ ʟᴀɴɢᴜᴀɢᴇ : <a href=https://www.python.org>ᴘʏᴛʜᴏɴ 3</a>
├➢ ᴅᴀᴛᴀʙᴀꜱᴇ : <a href=https://cloud.mongodb.com>MᴏɴɢᴏDB</a>
├➢ ꜱᴇʀᴠᴇʀ : <a href=https://apps.koyeb.com>ᴋᴏʏᴇʙ</a>
├➢ ʙᴜɪʟᴅ ꜱᴛᴀᴛᴜꜱ  : ᴘʏᴛʜᴏɴ v3.6.8
╰───────────────⍟

➢ ɴᴏᴛᴇ :- ᴘʟᴢ ᴅᴏɴ'ᴛ ᴀꜱᴋ ꜰᴏʀ ʀᴇᴘᴏ 🤡
</b>"""

HELP_TXT = """
🛸 <b><u>My Functions</u></b> 🛸
"""

Rename_TXT = """
<blockquote>✏️ <b><u>ʜᴏᴡ ᴛᴏ ʀᴇɴᴀᴍᴇ ᴀ ꜰɪʟᴇ</u></b></blockquote>
•> /rename ᴀғᴛᴇʀ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ sᴇɴᴅ ʏᴏᴜʀ ғɪʟᴇ ᴛᴏ ʀᴇɴᴀᴍᴇ.

<blockquote>🌌 <b><u>ʜᴏᴡ ᴛᴏ ꜱᴇᴛ ᴛʜᴜᴍʙɴᴀɪʟ</u></b></blockquote>
•> /set_thumb ꜱᴇɴᴅ ᴘɪᴄᴛᴜʀᴇ ᴛᴏ ꜱᴇᴛ ᴛʜᴜᴍʙɴᴀɪʟ.
•> /del_thumb ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴀɴᴅ ᴅᴇʟᴇᴛᴇ ʏᴏᴜʀ ᴏʟᴅ ᴛʜᴜᴍʙɴᴀɪʟ.
•> /view_thumb ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ᴠɪᴇᴡ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴛʜᴜᴍʙɴᴀɪʟ.

<blockquote>📑 <b><u>ʜᴏᴡ ᴛᴏ ꜱᴇᴛ ᴄᴜꜱᴛᴏᴍ ᴄᴀᴘᴛɪᴏɴ</u></b></blockquote>
•> /set_caption - ꜱᴇᴛ ᴀ ᴄᴜꜱᴛᴏᴍ ᴄᴀᴘᴛɪᴏɴ
•> /see_caption - ꜱᴇᴇ ʏᴏᴜʀ ᴄᴜꜱᴛᴏᴍ ᴄᴀᴘᴛɪᴏɴ
•> /del_caption - ᴅᴇʟᴇᴛᴇ ᴄᴜꜱᴛᴏᴍ ᴄᴀᴘᴛɪᴏɴ

ᴇxᴀᴍᴘʟᴇ:- /set_caption 📕 ꜰɪʟᴇ ɴᴀᴍᴇ: {ꜰɪʟᴇɴᴀᴍᴇ}
💾 ꜱɪᴢᴇ: {filesize}
⏰ ᴅᴜʀᴀᴛɪᴏɴ: {duration}
"""

STICKER_TXT = """
<b>⚝ ᴄᴏᴍᴍᴀɴᴅ : /stickerid

ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ꜰɪɴᴅ ᴀɴʏ ꜱᴛɪᴄᴋᴇʀ ɪᴅ. (Fᴏʀ ᴅᴇᴠᴇʟᴏᴘᴇʀs) 👨🏻‍💻
</b>"""

TELEGRAPH_TXT = """
<b>⚝ ᴜꜱᴀɢᴇ : /telegraph

ʀᴇᴘʟʏ ᴡɪᴛʜ /telegraph ᴏɴ ᴀ �ᴘɪᴄᴛᴜʀᴇ ᴏʀ ᴠɪᴅᴇᴏ ᴜɴᴅᴇʀ (5ᴍʙ) ᴛᴏ ɢᴇᴛ ᴀ ʟɪɴᴋ ʟɪᴋᴇ ᴛʜɪs 👇🏻

https://envs.sh/Fyw.jpg
</b>"""

RESTRICTED_TXT = """
> **💡 Restricted Content Saver**

**1. 🔒 Private Chats**
➥ For Owner Only :)

**2. 🌐 Public Chats**
➥ Simply share the post link. I'll download it for you.

**3. 📂 Batch Mode**
➥ Download multiple posts using this format:
> **https://t.me/xxxx/1001-1010**
"""

MERGER_TXT = """
<b>
> 📜 PDF Merging
• /merge - Start merging process
• Upload PDFs or Images in sequence
• /done - Merge all PDFs

> ⚠ Limitations
• Max File Size: 350 MB
• Max Files per Merge: 20

> ✨ Customizations
• Filename: Provide a custom name
• Custom Thumbnail: /set_thumb
</b>
"""

REQUEST_TXT = """
<b>
> ⚙️ Join Request Acceptor

• I can accept all pending join requests in your channel. 🤝

• Promote @xDzod and @Z900_RoBot with full admin rights in your channel. 🔑

• Send /accept command in the channel to accept all requests at once. 💯
</b>
"""

