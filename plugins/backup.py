import os

from pyrogram import Client, filters

import utils
from config import cmds


@Client.on_message(filters.command("backup", prefixes=".") & filters.me)
async def backup(client, message):
    await message.edit("Ok...")
    arq = await utils.backup_sources()
    await client.send_document(chat_id="me", document=arq)
    await message.edit("Completed")
    os.remove(arq)


cmds.update({".backup": "Make a backup"})
