from asyncio import sleep
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from config import START_PIC, ADMIN, REACTIONS
from helper.txt import mr
from helper.database import db
import random

FORCE_SUB_CHANNEL = "-1002448030573"

async def is_subscribed(user_id: int):
    try:
        status = await client.get_chat_member(FORCE_SUB_CHANNEL, user_id)
        return status.status in ["member", "administrator", "creator"]
    except Exception:
        return False

async def create_invite_link():
    try:
        # Check if the bot is an admin in the channel
        chat = await client.get_chat(FORCE_SUB_CHANNEL)
        if chat.type in ["channel", "supergroup"]:
            invite_link = await client.create_chat_invite_link(FORCE_SUB_CHANNEL, member_limit=1)
            return invite_link.invite_link
        else:
            print("Error: The provided FORCE_SUB_CHANNEL is not a valid channel or supergroup.")
            return None
    except Exception as e:
        print(f"Error creating invite link: {e}")
        return None

@Client.on_message(filters.private & filters.command("start"))
async def force_subscribe(client: Client, message: Message):
    user_id = message.from_user.id
    if not await is_subscribed(user_id):
        invite_link = await create_invite_link()
        if not invite_link:
            await message.reply_text("**❌ Error: Unable to generate invite link. Please contact the admin.**")
            return

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("Join Channel 🔔", url=invite_link)],
            [InlineKeyboardButton("Try Again 🔄", callback_data="check_subscription")]
        ])
        await message.reply_text(
            "**⚠️ You must join our channel to use this bot.**\n\n"
            "Please join the channel below and click **Try Again**.",
            reply_markup=buttons
        )
        return

    await start(client, message)

@Client.on_callback_query(filters.regex("check_subscription"))
async def check_subscription_callback(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    if await is_subscribed(user_id):
        await query.message.delete()
        await start(client, query.message)
    else:
        await query.answer("❌ You haven't joined the channel yet. Please join first!", show_alert=True)

    
# Original Start Command 
@Client.on_message(filters.private & filters.command("start"))
async def start(client, message):
    try:
        await message.react(emoji=random.choice(REACTIONS), big=True)
    except:
        pass     
    user = message.from_user
    if not await db.is_user_exist(user.id):
        await db.add_user(user.id)
    
    txt = (
        f"> **✨👋🏻 Hey {user.mention} !!**\n\n"
        f"**🔋 ɪ ᴀᴍ ᴀɴ ᴀᴅᴠᴀɴᴄᴇ ʙᴏᴛ ᴅᴇꜱɪɢɴᴇᴅ ᴛᴏ ᴀꜱꜱɪꜱᴛ ʏᴏᴜ ᴇꜰꜰᴏʀᴛʟᴇꜱꜱʟʏ.**\n\n"
        f"**🔘 Usᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ᴛᴏ ʟᴇᴀʀɴ ᴍᴏʀᴇ ᴀʙᴏᴜᴛ ᴍʏ ғᴜɴᴄᴛɪᴏɴs!**"
    )
    
    button = InlineKeyboardMarkup([
        [InlineKeyboardButton("🤖 ᴅᴇᴠᴇʟᴏᴘᴇʀ", url='https://t.me/axa_bachha')],
        [InlineKeyboardButton('📜 ᴀʙᴏᴜᴛ', callback_data='about'),
         InlineKeyboardButton('🕵🏻‍♀️ ʜᴇʟᴘ', callback_data='help')]
    ])
    
    if START_PIC:
        await message.reply_photo(START_PIC, caption=txt, reply_markup=button)
    else:
        await message.reply_text(text=txt, reply_markup=button, disable_web_page_preview=True)

# Logs Command
@Client.on_message(filters.command('logs') & filters.user(ADMIN))
async def log_file(client, message):
    try:
        await message.reply_document('TelegramBot.log')
    except Exception as e:
        await message.reply_text(f"Error:\n`{e}`")

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


# Callback Query Handler
@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    data = query.data
    
    if data == "start":
        txt = (
            f"> **✨👋🏻 Hey {query.from_user.mention} !!**\n\n"
            f"**🔋 ɪ ᴀᴍ ᴀɴ ᴀᴅᴠᴀɴᴄᴇ ʙᴏᴛ ᴅᴇꜱɪɢɴᴇᴅ ᴛᴏ ᴀꜱꜱɪꜱᴛ ʏᴏᴜ ᴇꜰꜰᴏʀᴛʟᴇꜱꜱʟʏ.**\n\n"
            f"**🔘 Usᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ᴛᴏ ʟᴇᴀʀɴ ᴍᴏʀᴇ ᴀʙᴏᴜᴛ ᴍʏ ғᴜɴᴄᴛɪᴏɴs!**"
        )
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🤖 ᴅᴇᴠᴇʟᴏᴘᴇʀ", url='https://t.me/axa_bachha')],
            [InlineKeyboardButton('📜 ᴀʙᴏᴜᴛ', callback_data='about'),
             InlineKeyboardButton('🕵🏻‍♀️ ʜᴇʟᴘ', callback_data='help')]
        ])
    
    elif data == "help":
        txt = mr.HELP_TXT
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("ᴄᴏɴᴛᴀᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ 🕵🏻‍♀️", url="https://t.me/axa_bachha")],
            [InlineKeyboardButton("ʀᴇᴏ̨ᴜᴇsᴛ ᴀᴄᴄᴇᴘᴛᴏʀ", callback_data="request"),
             InlineKeyboardButton("ᴍᴇʀɢᴇ 📄", callback_data="combiner")],
            [InlineKeyboardButton("ʀᴇsᴛʀɪᴄᴛᴇᴅ ᴄᴏɴᴛᴇɴᴛ sᴀᴠᴇʀ", callback_data="restricted")],
            [InlineKeyboardButton('ᴛᴇʟᴇɢʀᴀᴘʜ', callback_data='tele'),   
             InlineKeyboardButton('ꜱᴛɪᴄᴋᴇʀ-ɪᴅ', callback_data='sticker')],
            [InlineKeyboardButton('🏠 𝙷𝙾𝙼𝙴 🏠', callback_data='start')]
        ])
    
    elif data == "about":
        txt = mr.ABOUT_TXT.format(client.mention)
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🤖 ᴅᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/axa_bachha")],
            [InlineKeyboardButton("🔒 Close", callback_data="close"),
             InlineKeyboardButton("🏠 𝙷𝙾𝙼𝙴 🏠", callback_data="start")]
        ])
    
    elif data == "close":
        try:
            await query.message.delete()
            await query.message.reply_to_message.delete()
        except:
            await query.message.delete()
        return
    
    elif data == "sticker":
        txt = """<b>⚝ ᴄᴏᴍᴍᴀɴᴅ : /stickerid

ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ꜰɪɴᴅ ᴀɴʏ ꜱᴛɪᴄᴋᴇʀ ɪᴅ. (Fᴏʀ ᴅᴇᴠᴇʟᴏᴘᴇʀs) 👨🏻‍💻
 </b>"""
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="help"),
             InlineKeyboardButton("🤖 ᴅᴇᴠᴇʟᴏᴘᴇʀ", url="telegram.me/axa_bachha")]
        ])
    
    elif data == "tele":
        txt = """<b>
⚝ ᴜꜱᴀɢᴇ : /telegraph

ʀᴇᴘʟʏ ᴡɪᴛʜ /telegraph ᴏɴ ᴀ ᴘɪᴄᴛᴜʀᴇ ᴏʀ ᴠɪᴅᴇᴏ ᴜɴᴅᴇʀ (5ᴍʙ) ᴛᴏ ɢᴇᴛ ᴀ ʟɪɴᴋ ʟɪᴋᴇ ᴛʜɪs 👇🏻

https://envs.sh/Fyw.jpg
 </b>"""
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="help"),
             InlineKeyboardButton("🤖 ᴅᴇᴠᴇʟᴏᴘᴇʀ", url="telegram.me/axa_bachha")]
        ])
    
    await query.message.edit_text(text=txt, reply_markup=reply_markup, disable_web_page_preview=True)


# Additional Callback Queries
CALLBACK_TEXTS = {
    "restricted": "> **💡 Restricted Content Saver**\n\n"
                   "**1. 🔒 Private Chats**\n➥ Currently not working. 🙁\n\n"
                   "**2. 🌐 Public Chats**\n➥ Simply share the post link. I'll download it for you.\n\n"
                   "**3. 📂 Batch Mode**\n➥ Download multiple posts using this format: \n"
                   "https://t.me/xxxx/1001-1010",

    "combiner": "> **📜 𝑃𝐷𝐹 𝑀𝑒𝑟𝑔𝑖𝑛𝑔 :**\n\n"
                 "•/merge - 𝑆𝑡𝑎𝑟𝑡 𝑚𝑒𝑟𝑔𝑖𝑛𝑔 𝑝𝑟𝑜𝑐𝑒𝑠𝑠\n"
                 "•𝑈𝑝𝑙𝑜𝑎𝑑 𝑃𝐷𝐹𝑠 𝑜𝑟 𝐼𝑚𝑎𝑔𝑒𝑠 𝑖𝑛 𝑠𝑒𝑞𝑢𝑒𝑛𝑐𝑒\n"
                 "•/done : 𝑀𝑒𝑟𝑔𝑒 𝑎𝑙𝑙 𝑃𝐷𝐹𝑠\n\n"
                 "> **⚠ 𝐿𝑖𝑚𝑖𝑡𝑎𝑡𝑖𝑜𝑛𝑠 : **\n"
                 "•𝑀𝑎𝑥 𝐹𝑖𝑙𝑒 𝑆𝑖𝑧𝑒: 20𝑀𝐵\n"
                 "•𝑀𝑎𝑥 𝐹𝑖𝑙𝑒𝑠 𝑝𝑒𝑟 𝑀𝑒𝑟𝑔𝑒: 20\n\n"
                 "> **✨ 𝑪𝒖𝒔𝒕𝒐𝒎𝒊𝒛𝒂𝒕𝒊𝒐𝒏𝒔 :**\n"
                 "• 𝐹𝑖𝑙𝑒𝑛𝑎𝑚𝑒: 𝑃𝑟𝑜𝑣𝑖𝑑𝑒 𝑎 𝑐𝑢𝑠𝑡𝑜𝑚 𝑛𝑎𝑚𝑒\n"
                 "• 𝑇ℎ𝑢𝑚𝑏𝑛𝑎𝑖𝑙: 𝑈𝑠𝑒 (𝐹𝑖𝑙𝑒𝑛𝑎𝑚𝑒) -t (𝑇ℎ𝑢𝑚𝑏𝑛𝑎𝑖𝑙 𝑙𝑖𝑛𝑘)",

    "request": "> **⚙️ Join Request Acceptor**\n\n"
                "**• 𝐼 𝑐𝑎𝑛 𝑎𝑐𝑐𝑒𝑝𝑡 𝑎𝑙𝑙 𝑝𝑒𝑛𝑑𝑖𝑛𝑔 𝑗𝑜𝑖𝑛 𝑟𝑒𝑞𝑢𝑒𝑠𝑡𝑠 𝑖𝑛 𝑦𝑜𝑢𝑟 𝑐ℎ𝑎𝑛𝑛𝑒𝑙. **🤝\n\n"
                "**• 𝑃𝑟𝑜𝑚𝑜𝑡𝑒 @Axa_bachha 𝑎𝑛𝑑 @Z900_RoBot 𝑤𝑖𝑡ℎ 𝑓𝑢𝑙𝑙 𝑎𝑑𝑚𝑖𝑛 𝑟𝑖𝑔ℎ𝑡𝑠 𝑖𝑛 𝑦𝑜𝑢𝑟 𝑐ℎ𝑎𝑛𝑛𝑒𝑙. **🔑\n\n"
                "**• 𝑆𝑒𝑛𝑑 /accept 𝑐𝑜𝑚𝑚𝑎𝑛𝑑 𝑖𝑛 𝑐ℎ𝑎𝑛𝑛𝑒𝑙 𝑡𝑜 𝑎𝑐𝑐𝑒𝑝𝑡 𝑎𝑙𝑙 𝑟𝑒𝑞𝑢𝑒𝑠𝑡𝑠 𝑎𝑡 𝑜𝑛𝑐𝑒. 💯**"
}

@Client.on_callback_query(filters.regex("restricted|combiner|request"))
async def callback_text_handler(client: Client, query: CallbackQuery):
    await query.answer()
    await query.message.edit_text(
        text=CALLBACK_TEXTS[query.data],
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="help")]
        ]),
        disable_web_page_preview=True
    )
