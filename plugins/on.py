import json
import time
from datetime import datetime

from config import cmds

from pyrogram import Client, Filters


@Client.on_message(Filters.command(["on", "off"], prefixes=".") & Filters.me)
async def on(client, message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif message.entities and 'text_mention' in message.entities[0]['type']:
        user_id = message.entities[0].user.id
    # User ids: integers
    elif message.command[1].isdigit():
        user_id = int(message.command[1])
    # Usernames and phone numbers with +
    else:
        user_id = message.command[1]
    usr = await client.get_users(user_id)
    if usr.is_bot:
        await message.edit('does not work with bots')
    elif usr.status == 'online':
        await message.edit(f'<a href="tg://user?id={usr.id}">{usr.first_name}</a> is on')
    elif not usr.last_online_date:
        await message.edit('This person has disabled his last seen')
    else:
        c = int(time.time() - usr.last_online_date)
        date = datetime.utcfromtimestamp(c).strftime(
            '{"year":"%y","months":"%-m","days":"%-d","hours":"%-H","minutes":"%-M","seconds":"%-S"}')
        frase = f'<a href="tg://user?id={usr.id}">{usr.first_name}</a> is off for: \n'
        date = json.loads(date)
        date["year"] = int(date["year"][1])
        date["days"] = int(date["days"]) - 1
        date["months"] = int(date["months"]) - 1
        if date["year"] != 0:
            frase += f' » **{date["year"]}** year\n'
        if date["months"] != 0:
            frase += f' » **{date["months"]}** months\n'
        if date["days"] != 0:
            frase += f' » **{date["days"]}** Days\n'
        if date["hours"] != "0":
            frase += f' » **{date["hours"]}** Hours\n'
        if date["minutes"] != "0":
            frase += f' » **{date["minutes"]}** Minutes\n'
        if date["seconds"] != "0":
            frase += f' » **{date["seconds"]}** Seconds'
        await message.edit(frase)

cmds.update({'.on':'Check if the person is online'})
