from pyrogram import Client, Filters
from datetime import datetime

@Client.on_message(Filters.command("ping", prefixes = '.') & Filters.me)
def ping(client,message):
    t1 = datetime.now()
    a = message.reply_text('**Pong!**')
    t2 = datetime.now()
    message.edit(f'**Pong!** `{(t2 - t1).microseconds / 1000}`ms')
    a.delete()
