from pyrogram import Client, Filters
from time import sleep

@Client.on_message(Filters.command("text", prefixes=".") & Filters.me)
def ping(client,message):
    ch = ''
    text = message.text.split(' ',1)[1]
    ms = message.edit('`|`')
    for i in text:
        ch = ch + i
        ms.edit(f'`{ch}`')
        sleep(0.3)
        ms.edit(f'`{ch}|`')
        sleep(0.3)
    ms.edit(f'`{text}`')