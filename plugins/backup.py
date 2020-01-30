import os

from pyrogram import Client, Filters

import utils


@Client.on_message(Filters.command("backup", prefixes='.') & Filters.me)
def backup(client, message):
    message.edit('Ok...')
    arq = utils.backup_sources()
    client.send_document(chat_id="me", document=arq)
    message.edit('Completed')
    os.remove(arq)
