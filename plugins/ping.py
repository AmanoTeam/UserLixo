from datetime import datetime

from config import cmds

from pyrogram import Client, Filters


@Client.on_message(Filters.command("ping", prefixes='.') & Filters.me)
async def ping(client, message):
    t1 = datetime.now()
    a = await message.reply_text('**Pong!**')
    t2 = datetime.now()
    await message.edit(f'**Pong!** `{(t2 - t1).microseconds / 1000}`ms')
    await a.delete()

cmds.update({'.ping':'View server ping'})
