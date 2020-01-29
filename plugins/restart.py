import os
import sys

from pyrogram import Client, Filters

from db import db, save


@Client.on_message(Filters.command("restart", prefixes=".") & Filters.me)
def restart(client, message):
    message.edit('Reiniciando...')
    db["restart"] = {'cid': message.chat.id, 'mid': message.message_id}
    save(db)
    os.execl(sys.executable, sys.executable, *sys.argv)
