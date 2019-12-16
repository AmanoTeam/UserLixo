from pyrogram import Client, Filters
import time
import re
import os
import chromeprinter

a = chromeprinter.Client()

@Client.on_message(Filters.command("print", prefixes = ['!','/']))
def print(client, message):
    url = message.text.split(' ',1)[1]
    ctime = time.time()
    if re.match(r'^[a-z]+://', url):
        url = url
    else:
        url = 'http://'+url
    a.make_screenshot(url,f'{ctime}.png')
    client.send_photo(message.chat.id,f"{ctime}.png")
    os.remove(f'{ctime}.png')