import os
import time

from config import cmds

from gtts import gTTS, lang
from pyrogram import Client, Filters


@Client.on_message(Filters.command("tts", prefixes=".") & Filters.me)
async def tts(client, message):
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
        if message.reply_to_message.text:
            txt = message.reply_to_message.text
        elif message.reply_to_message.document:
            path = await message.reply_to_message.download(f'{message.message_id}_{message.reply_to_message.message_id}_tts')
            with open(path) as fp:
                txt = fp.read()
                os.remove(fp.name)
        else:
            return await message.edit('Nothing to use')
    gtts = gTTS(txt, lang=langs)
    ctime = time.time()
    gtts.save(f'{ctime}.mp3')
    await message.delete()
    if message.reply_to_message:
        await client.send_voice(message.chat.id, f'{ctime}.mp3', reply_to_message_id=message.reply_to_message.message_id)
    else:
        await client.send_voice(message.chat.id, f'{ctime}.mp3')
    os.remove(f'{ctime}.mp3')

cmds.update({'.tts':'Convert text to speech with Google APIs'})
