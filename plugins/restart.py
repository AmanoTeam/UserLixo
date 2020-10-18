import os
import sys

from pyrogram import Client, filters

from db import db, save
from config import cmds


@Client.on_message(filters.command("restart", prefixes=".") & filters.me)
async def restart(client, message):
    await message.edit('Reiniciando...')
    db["restart"] = {'cid': message.chat.id, 'mid': message.message_id}
    save(db)
    os.execl(sys.executable, sys.executable, *sys.argv)

cmds.update({'.restart':'Restart a bot'})
