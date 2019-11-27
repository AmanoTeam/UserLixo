from pyrogram import Client, Filters
from datetime import datetime

@Client.on_message(Filters.command("ping", prefixes = ['/','!']))
def ping(client,message):
    t1 = datetime.now()
    a = message.reply_text('**Pong!**')
    t2 = datetime.now()
    a.edit(f'**Pong!** `{(t2 - t1).microseconds / 1000}`ms')
