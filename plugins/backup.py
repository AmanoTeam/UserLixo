import os
import utils

from pyrogram import Client, Filters
from config import cmds

@Client.on_message(Filters.command("backup", prefixes='.') & Filters.me)
async def backup(client, message):
    await message.edit('Ok...')
    arq = await utils.backup_sources()
    await client.send_document(chat_id="me", document=arq)
    await message.edit('Completed')
    os.remove(arq)
    
cmds.update({'.backup':'Make a backup'})
