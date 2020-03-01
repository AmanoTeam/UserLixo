from pyrogram import Client, Filters
from config import cmds
from utils import switch_case
import re

@client.on_message(Filters.regex("s/(?P<search>.+)/(?P<replace>.+)(?:/(?P<flags>.+))") & Filters.me)
async def onsed(client, message):
    if not message.reply_to_message or not message.reply_to_message.from_user or message.reply_to_message.from_user.id != (await client.get_me()).id:
        return
    match = message.matches[0]
    flags = 0
    if 'flags' in match:
        for flag in match['flags']:
            flag = switch_case(flag.lower(), {
                'i': re.I,
                's': re.S,
                'm': re.M,
                'a': re.A,
                'l': re.L,
                'x': re.X,
            })
            if flag != None:
                flags |= flag
    text = message.reply_to_message.text.html
    text = re.sub(match['search'], message['replace'], 0, flags)
    await message.reply_to_message.edit(text, parse_mode="HTML")