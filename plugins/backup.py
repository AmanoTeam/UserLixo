import config
import utils
from pyrogram import Client, Filters
import os

@Client.on_message(Filters.command("backup", prefixes = '!') & Filters.me)
def backup(client, message):
    if message.from_user.id in config.sudos:
        mess = message.reply('Ok...')
        cid = message.chat.id
        arq = utils.backup_sources()
        if 'privado' in message.text or 'pv' in message.text:
            cid = message.from_user.id
        client.send_document(chat_id=cid,document=arq)
        mess.edit('Completed')
        os.remove(arq)