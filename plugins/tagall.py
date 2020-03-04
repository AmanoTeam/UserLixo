from pyrogram import Client, Filters

from config import cmds
import html
char = html.unescape('&#8204;')

@Client.on_message(Filters.command("tagall", prefixes=".") & Filters.me)
async def tagall(client, message):
    await message.delete()
    
    splitted = message.text.split(' ', 1)
    if len(splitted) < 2:
        a = ''
    else:
        a = splitted[1]
    
    async for x in client.iter_chat_members(message.chat.id):
        if x.user.status == 'online':
            a += f"[{char}](tg://user?id={x.user.id})"
    kwargs = {}
    if message.reply_to_message:
        kwargs['reply_to_message_id'] = message.reply_to_message.message_id
    await client.send_message(message.chat.id, a, **kwargs)

@Client.on_message(Filters.command("ftagall", prefixes=".") & Filters.me)
async def ftagall(client, message):
    await message.delete()
    
    splitted = message.text.split(' ', 1)
    if len(splitted) < 2:
        a = ''
    else:
        a = splitted[1]
        
    async for x in client.iter_chat_members(message.chat.id):
        if x.user.is_bot == False and x.user.is_deleted == False:
            a += f"[{char}](tg://user?id={x.user.id})"
    kwargs = {}
    if message.reply_to_message:
        kwargs['reply_to_message_id'] = message.reply_to_message.message_id
    await client.send_message(message.chat.id, a, **kwargs)


@Client.on_message(Filters.command("admin", prefixes=".") & Filters.me)
async def admin(client, message):
    await message.delete()
    
    splitted = message.text.split(' ', 1)
    if len(splitted) < 2:
        a = '@admin'
    else:
        a = splitted[1]
    
    async for x in client.iter_chat_members(message.chat.id, filter='administrators'):
        if x.user.status == 'online':
            a += f"[{char}](tg://user?id={x.user.id})"
    kwargs = {}
    if message.reply_to_message:
        kwargs['reply_to_message_id'] = message.reply_to_message.message_id
    await client.send_message(message.chat.id, a, **kwargs)

@Client.on_message(Filters.command("fadmin", prefixes=".") & Filters.me)
async def fadmin(client, message):
    await message.delete()
    
    splitted = message.text.split(' ', 1)
    if len(splitted) < 2:
        a = '@admin'
    else:
        a = splitted[1]
        
    async for x in client.iter_chat_members(message.chat.id, filter='administrators'):
        if x.user.is_bot == False and x.user.is_deleted == False:
            a += f"[{char}](tg://user?id={x.user.id})"
    
    kwargs = {}
    if message.reply_to_message:
        kwargs['reply_to_message_id'] = message.reply_to_message.message_id
    await client.send_message(message.chat.id, a, **kwargs)

cmds.update({'.tagall':'Mark all online members of the group',
             '.ftagall':'Mark all members of the group',
             '.admin':'Mark all online admins of the group',
             '.fadmin':'Mark all admins of the group'})
