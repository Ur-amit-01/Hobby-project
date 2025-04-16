import os
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserAlreadyParticipant, InviteRequestSent
from config import API_ID, API_HASH, BOT_TOKEN, NEW_REQ_MODE, SESSION_STRING

@Client.on_message(filters.command('accept'))
async def accept(client, message):
    # Log the chat type for debugging
    print(f"Received message from chat: {message.chat.type}")

    # Check if the command is issued in a private chat (DM)
    if message.chat.type == enums.ChatType.PRIVATE:
        print("Command issued in DM, sending reply...")
        return await message.reply("🚫 **This command works in channels only.**")
    
    # Proceed if the command is issued in a channel
    channel_id = message.chat.id
    show = await client.send_message(channel_id, "⏳ **Please wait...**")
    
    try:
        # Check if the bot has required permissions
        bot_member = await client.get_chat_member(channel_id, (await client.get_me()).id)
        bot_permissions = bot_member.privileges
        
        if not (bot_permissions and bot_permissions.can_invite_users and bot_permissions.can_promote_members):
            return await show.edit("❌ **I need 'Invite Users' and 'Add New Admins' permissions to work properly.**")
        
    except Exception as e:
        return await show.edit(f"❌ **Could not verify permissions: {str(e)}**")
    
    try:
        acc = Client("joinrequest", session_string=SESSION_STRING, api_hash=API_HASH, api_id=API_ID)
        await acc.start()
    except Exception as e:
        return await show.edit(f"❌ **Login session has expired or error occurred: {str(e)}**")
    
    # Add session account to the channel
    try:
        user_info = await acc.get_me()
        user_id = user_info.id
        user_name = user_info.username or user_info.first_name
        
        msg = await show.edit(f"👤 **Adding {user_name} to the channel...**")
        
        try:
            # Try to add the user to the channel
            chat_link = await client.create_chat_invite_link(channel_id)
            await acc.join_chat(chat_link.invite_link)
            await msg.edit(f"✅ **{user_name} joined the channel. Now accepting join requests...**")
        except UserAlreadyParticipant:
            await msg.edit(f"✅ **{user_name} is already in the channel. Now accepting join requests...**")
        except Exception as e:
            return await msg.edit(f"❌ **Could not add session account to channel: {str(e)}**")
        
        # Accept all join requests
        try:
            while True:
                await acc.approve_all_chat_join_requests(channel_id)
                await asyncio.sleep(1)
                join_requests = [request async for request in acc.get_chat_join_requests(channel_id)]
                if not join_requests:
                    break
            
            await msg.edit("🎉 **Successfully accepted all join requests!**")
        except Exception as e:
            await msg.edit(f"⚠️ **An error occurred while accepting requests: {str(e)}**")
        
        # Leave the channel
        try:
            await acc.leave_chat(channel_id)
            await msg.edit("✅ **All join requests accepted and session account has left the channel!**")
        except Exception as e:
            await msg.edit(f"⚠️ **Accepted all requests but failed to leave channel: {str(e)}**")
        
    except Exception as e:
        await msg.edit(f"⚠️ **An error occurred: {str(e)}**")
    finally:
        await acc.stop()


@Client.on_chat_join_request(filters.group | filters.channel)
async def approve_new(client, m):
    if not NEW_REQ_MODE:
        return  # If NEW_REQ_MODE is False, the function exits without processing the join request.

    try:
        await client.approve_chat_join_request(m.chat.id, m.from_user.id)
        try:
            await client.send_message(
                m.from_user.id,
                f"👋 **Hello {m.from_user.mention}!\nWelcome to {m.chat.title}**\n\n__Powered by: @VJ_Botz__"
            )
        except:
            pass
    except Exception as e:
        print(f"⚠️ {str(e)}")
        pass
