from pyrogram import Client, Filters
from config import sudos
from db import db,save
import os
import sys
import threading
import time

@Client.on_message(Filters.command("restart", prefixes="!"))
def restart(client, message):
    if message.from_user.id in sudos:
        sent = message.reply('Reiniciando...')
        db["restart"] = {'cid':message.chat.id, 'mid':sent.message_id}
        save(db)
        time.sleep(1)
        os.execl(sys.executable, sys.executable, *sys.argv)
        del threading.Thread