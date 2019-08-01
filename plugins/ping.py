from pyrogram import Client, Filters
from datetime import datetime

@Client.on_message(Filters.command("ping", prefix = ['/','!',''], separator = '.'))
def ping(client,message):
    t1 = datetime.now()
    a = message.reply('**Pong!**')
    t2 = datetime.now()
    a.edit(f'**Pong!** `{(t1 - t2).microseconds / 1000}`ms')