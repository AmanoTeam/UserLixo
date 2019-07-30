from pyrogram import Client, Filters
import time

@Client.on_message(Filters.command("ping", prefix = ['/','!'], separator = '.'))
def ping(client,message):
    t1 = time.time()
    a = message.reply('**Pong!**')
    t2 = time.time()
    a.edit(f'**Pong!** `{round((t2 - t1),3)}`s')