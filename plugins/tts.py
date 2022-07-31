import logging
import os
from io import BytesIO

from gtts import gTTS, lang
from pyrogram import Client, filters
from pyrogram.types import Message

from config import cmds

try:
    langs = lang.tts_langs()
except RuntimeError:
    logging.warning(
        f"[{__name__}] Unable to cache the list of tts languages. Will be tried again in the first time you use the command."
    )
    langs = None


@Client.on_message(filters.command("tts", prefixes=".") & filters.me)
async def tts(client: Client, message: Message):
    global langs
    if not langs:
        langs = lang.tts_langs()
    text: str = None
    mtext = message.text[5:]
    if "|" in mtext:
        tlang, text = mtext.split("|", 1)
    else:
        if mtext in langs:
            tlang = mtext
        else:
            text = mtext
            tlang = "pt-BR"
    if not text and message.reply_to_message:
        if message.reply_to_message.text:
            text = message.reply_to_message.text
        elif message.reply_to_message.document:
            path = await message.reply_to_message.download(
                f"{message.id}_{message.reply_to_message.id}_tts"
            )
            with open(path) as fp:
                text = fp.read()
            os.remove(path)
        else:
            return await message.edit_text("Nothing to use")
    gtts = gTTS(text, lang=tlang)
    bio = BytesIO()
    bio.name = "audio.mp3"
    try:
        gtts.write_to_fp(bio)
    except ValueError as e:
        await message.edit_text(f"Error: {e}", disable_web_page_preview=True)
    else:
        await message.delete()
        reply_to = message.reply_to_message.id if message.reply_to_message else None
        await client.send_voice(message.chat.id, bio, reply_to_message_id=reply_to)


cmds.update({".tts": "Convert text to speech with Google APIs"})
