import os
import time

from gtts import gTTS, lang
from pyrogram import Client, Filters


@Client.on_message(Filters.command("tts", prefixes=".") & Filters.me)
def tts(client, message):
    langs = False
    txt = False
    a = message.text[5:]
    if '|' in a:
        langs, txt = a.split('|', 1)
    else:
        if a in lang.tts_langs():
            langs = a
        else:
            txt = a
    if not langs:
        langs = 'pt-BR'
    if not txt and message.reply_to_message:
        txt = message.reply_to_message.text
    gtts = gTTS(txt, lang=langs)
    ctime = time.time()
    gtts.save(f'{ctime}.mp3')
    message.delete()
    if message.reply_to_message:
        client.send_voice(message.chat.id, f'{ctime}.mp3', reply_to_message_id=message.reply_to_message.message_id)
    else:
        client.send_voice(message.chat.id, f'{ctime}.mp3')
    os.remove(f'{ctime}.mp3')
