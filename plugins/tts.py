from gtts import gTTS
from pyrogram import Client, Filters
import os
import time 


@Client.on_message(Filters.command("tts", prefixes=".") & Filters.me)
def oi(client, message):
    if message.reply_to_message:
        txt = message.reply_to_message.text
        lang = message.text[5:]
    else:
        a = message.text[5:]
        lang, txt = a.split(' ',1)
    tts = gTTS(txt, lang=lang)
    ctime = time.time()
    tts.save(f'{ctime}.mp3')
    message.delete()
    client.send_voice(message.chat.id,f'{ctime}.mp3')
    os.remove(f'{ctime}.mp3')