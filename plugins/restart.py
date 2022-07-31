import os
import sys

from pyrogram import Client, filters
from pyrogram.types import Message

from config import cmds
from db import db, save


@Client.on_message(filters.command("restart", prefixes=".") & filters.me)
async def restart(client: Client, message: Message):
    await message.edit("Reiniciando...")
    db["restart"] = {"cid": message.chat.id, "mid": message.id}
    save(db)
    os.execl(sys.executable, sys.executable, *sys.argv)


cmds.update({".restart": "Restart a bot"})
