from pyrogram import Client, Filters
import requests
import time
import re
import os

@Client.on_message(Filters.command("print", prefix = ['!','/'], separator = ' '))
def print(client, message):
    url = message.text.split(' ',1)[1]
    ctime = time.time()
    try:
        if not re.match(r'^[a-z]+://', url):
            url = 'http://'+url
        r = requests.post("https://api.olixao.ml/print", params=dict(q=url))
        with open(f'{ctime}.png', 'wb') as f:
            f.write(r.content)
        client.send_photo(message.chat.id,f"{ctime}.png")
    except Exception as e:
        message.reply(f'There was an error sending print, please try again later. \nDescription of the error:{e}')
    os.remove(f'{ctime}.png')