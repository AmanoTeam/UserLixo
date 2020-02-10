from time import sleep

from pyrogram import Client, Filters


@Client.on_message(Filters.command("text", prefixes=".") & Filters.me)
async def text(client, message):
    ch = ''
    txt = message.text.split(' ', 1)[1]
    ms = await message.edit('`|`')
    for i in txt:
        ch += i
        ms = await ms.edit(f'`{ch}|`')
        sleep(0.3)
        ms = await ms.edit(f'`{ch.strip()}`')
        sleep(0.3)
