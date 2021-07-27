from pyrogram import Client, filters
from telegraph import Telegraph

from config import cmds

import desciclopedia
import wikipedia

telegraph = Telegraph()
telegraph.create_account(short_name="UserLixo", author_name="amn")

@Client.on_message(filters.command("dwiki", prefixes='.') & filters.me)
async def dwiki(client, message):
    txt = message.text[7:]
    a = desciclopedia.search(txt)
    if a:
        a = desciclopedia.page(a[0])
        response = telegraph.create_page(
            a.title,
            html_content=a.content,
            author_name="Desciclopedia",
            author_url=a.url
        )
        await message.edit(response["url"])
    else:
        await message.edit(f"No results found for \"`{txt}`\"")


@Client.on_message(filters.command("wiki", prefixes='.') & filters.me)
async def wiki(client, message):
    txt = message.text[6:]
    a = wikipedia.search(txt)
    wikipedia.set_lang('pt')
    if a:
        a = wikipedia.page(a[0])
        response = telegraph.create_page(
            a.title,
            html_content=a.content,
            author_name="Wikipedia",
            author_url=a.url
        )
        await message.edit(response["url"])
    else:
        await message.edit(f"No results found for \"`{txt}`\"")

cmds.update({'.wiki':'Search meaning of a word on wikipedia',
             '.dwiki':'Search meaning of a word on desciclopedia'})
