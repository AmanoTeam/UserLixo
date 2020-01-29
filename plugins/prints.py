import os
import re
import time

import chromeprinter
from pyrogram import Client, Filters

a = chromeprinter.Client()


@Client.on_message(Filters.command("print", prefixes=".") & Filters.me)
def prints(client, message):
    url = message.text.split(' ', 1)[1]
    message.edit(f'printing: {url}')
    ctime = time.time()
    if re.match(r'^[a-z]+://', url):
        url = url
    else:
        url = 'http://' + url
    a.make_screenshot(url, f'{ctime}.png')
    try:
        client.send_photo(message.chat.id, f"{ctime}.png")
    finally:
        os.remove(f'{ctime}.png')
    message.delete()
