import json
import time
from datetime import datetime

from pyrogram.enums import MessageEntityType, UserStatus
from pyrogram import Client, filters
from pyrogram.types import Message

from config import cmds


@Client.on_message(filters.command(["on", "off"], prefixes=".") & filters.me)
async def on(client: Client, message: Message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif message.entities and message.entities[0].type == MessageEntityType.TEXT_MENTION:
        user_id = message.entities[0].user.id
    # User ids: integers
    elif message.command[1].isdigit():
        user_id = int(message.command[1])
    # Usernames and phone numbers with +
    else:
        user_id = message.command[1]
    usr = await client.get_users(user_id)
    if usr.is_bot:
        await message.edit("does not work with bots")
    elif usr.status == UserStatus.ONLINE:
        await message.edit(
            f'<a href="tg://user?id={usr.id}">{usr.first_name}</a> is on'
        )
    elif not usr.last_online_date:
        await message.edit("This person has disabled his last seen")
    else:
        c = datetime.now() - usr.last_online_date
        frase = f'<a href="tg://user?id={usr.id}">{usr.first_name}</a> is off for: \n'
        days = c.days
        years = days // 365
        months = (days % 365) // 30
        days = days % 30
        if years != 0:
            frase += f' » **{years}** year\n'
        if months != 0:
            frase += f' » **{months}** months\n'
        if days != 0:
            frase += f' » **{days}** Days\n'
        if c.seconds // 3600 != 0:
            frase += f' » **{c.seconds // 3600}** Hours\n'
        if (c.seconds // 60) % 60 != 0:
            frase += f' » **{(c.seconds // 60) % 60}** Minutes\n'
        if c.seconds % 60 != 0:
            frase += f' » **{c.seconds % 60}** Seconds'
        await message.edit(frase)


cmds.update({".on": "Check if the person is online"})
