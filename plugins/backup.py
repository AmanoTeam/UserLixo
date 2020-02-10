import os

from pyrogram import Client, Filters

import utils


@Client.on_message(Filters.command("backup", prefixes='.') & Filters.me)
async def backup(client, message):
    await message.edit('Ok...')
    arq = utils.backup_sources()
    await client.send_document(chat_id="me", document=arq)
    await message.edit('Completed')
    os.remove(arq)
