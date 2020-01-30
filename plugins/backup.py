import os

from pyrogram import Client, Filters

import utils


@Client.on_message(Filters.command("backup", prefixes='.') & Filters.me)
def backup(client, message):
    mess = message.reply('Ok...')
    arq = utils.backup_sources()
    client.send_document(chat_id="me", document=arq)
    mess.edit('Completed')
    os.remove(arq)
