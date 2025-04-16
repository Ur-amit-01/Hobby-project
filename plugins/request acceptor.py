import os
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPrivileges
from pyrogram.errors import UserAlreadyParticipant, ChatAdminRequired, UserNotParticipant
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
    
    # Check if bot has required permissions
    try:
        bot_member = await client.get_chat_member(channel_id, "me")
        bot_permissions = bot_member.privileges
        
        if not (bot_permissions.can_invite_users and bot_permissions.can_promote_members):
            return await show.edit("❌ **I need 'Invite Users' and 'Add New Admins' permissions to perform this operation.**")
    except Exception as e:
        return await show.edit(f"❌ **Error checking bot permissions: {str(e)}**")
    
    # Initialize session client
    try:
        acc = Client("joinrequest", session_string=SESSION_STRING, api_hash=API_HASH, api_id=API_ID)
        await acc.start()
        user_info = await acc.get_me()
        user_id = user_info.id
        username = user_info.username or user_info.first_name
    except Exception as e:
        return await show.edit(f"❌ **Login session has expired or error occurred: {str(e)}**")
    
    await show.edit("🔄 **Setting up the process...**")
    
    # Generate an invite link for the channel
    try:
        invite_link = await client.create_chat_invite_link(channel_id)
        invite_url = invite_link.invite_link
        await show.edit(f"✅ **Created invite link. Asking user to join...**")
    except Exception as e:
        await acc.stop()
        return await show.edit(f"❌ **Failed to create invite link: {str(e)}**")
    
    # Have the session account join using the invite link
    try:
        try:
            # Check if already in channel
            try:
                await acc.get_chat_member(channel_id, user_id)
                await show.edit("✅ **User already in the channel. Proceeding...**")
            except UserNotParticipant:
                await acc.join_chat(invite_url)
                await show.edit("✅ **User joined the channel. Promoting to admin...**")
        except Exception as e:
            await acc.stop()
            return await show.edit(f"❌ **Failed to join channel: {str(e)}**")
    except Exception as e:
        await acc.stop()
        return await show.edit(f"❌ **Failed to check or join channel: {str(e)}**")
    
    # Promote session account to admin with required permissions
    try:
        await client.promote_chat_member(
            channel_id, 
            user_id,
            privileges=ChatPrivileges(
                can_invite_users=True,
                can_manage_chat=True,
                can_change_info=False,
                can_delete_messages=False,
                can_manage_video_chats=False,
                can_restrict_members=False,
                can_promote_members=False,
                can_pin_messages=False,
                can_edit_messages=False
            )
        )
        await show.edit("✅ **User promoted to admin. Now accepting join requests...**")
    except Exception as e:
        await acc.stop()
        return await show.edit(f"❌ **Failed to promote user: {str(e)}**")
    
    # Accept all join requests
    try:
        msg = await show.edit("✅ **Accepting all join requests... Please wait until it's completed.**")
        requests_count = 0
        
        while True:
            try:
                join_requests = [request async for request in acc.get_chat_join_requests(channel_id)]
                if not join_requests:
                    break
                
                await acc.approve_all_chat_join_requests(channel_id)
                requests_count += len(join_requests)
                await asyncio.sleep(1)
            except Exception as e:
                await msg.edit(f"⚠️ **Error while accepting requests: {str(e)}**")
                break
        
        await msg.edit(f"🎉 **Successfully accepted {requests_count} join requests!**")
    except Exception as e:
        await msg.edit(f"⚠️ **An error occurred while accepting requests: {str(e)}**")
    
    # Leave the channel
    try:
        await asyncio.sleep(2)  # Small delay before leaving
        await acc.leave_chat(channel_id)
        await msg.edit(f"✅ **Mission completed! Accepted {requests_count} join requests and left the channel.**")
    except Exception as e:
        await msg.edit(f"✅ **Accepted {requests_count} join requests, but failed to leave the channel: {str(e)}**")
    
    # Stop the client session
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
                f"**• Hello {m.from_user.mention}! 👋🏻\n• Your request for {m.chat.title} is accepted.**\n\n> **• Powered by: @Stellar_Bots x @Team_SAT_25**"
            )
        except:
            pass
    except Exception as e:
        print(f"⚠️ {str(e)}")
        pass
