import logging
import os
from io import BytesIO

from gtts import gTTS, lang
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from config import bot, user

try:
    langs = lang.tts_langs()
except RuntimeError:
    logging.warning(
        f"[{__name__}] Unable to cache the list of tts languages. Will be tried again in the first time you use the command."
    )
    langs = None


@Client.on_message(filters.command("tts", prefixes=".") & filters.me)
async def tts(c: Client, m: Message):
    global langs
    if not langs:
        langs = lang.tts_langs()
    table = []
    row = []
    for i, lang in enumerate(langs):
        if i % 3 == 0 and i != 0:
            table.append(row)
            row = []
        row.append((lang, f"tts_{m.chat.id}_{m.id}_{lang}"))
    table.append(row)
    
    await m.reply("Choose a language", reply_markup=table)

@bot.on_callback_query(filters.regex(r"tts") & filters.sudoers)
async def tts_callback(_, q: CallbackQuery):
    chat_id, message_id, tlang = q.data.split("_")[1:]
    message = await user.get_messages(chat_id, int(message_id))
    global langs
    text: str = None
    mtext = message.text.split(" ", 1)
    if len(mtext) > 1:
        text = mtext[1]
    if not text and message.reply_to_message:
        if message.reply_to_message.text:
            text = message.reply_to_message.text
        if message.reply_to_message.caption:
            text = message.reply_to_message.caption
        elif message.reply_to_message.document:
            path = await message.reply_to_message.download(
                f"{message.id}_{message.reply_to_message.id}_tts"
            )
            with open(path) as fp:
                text = fp.read()
            os.remove(path)
    if not text:
        return await q.edit("Nothing to use")
    resp = await atts(text, tlang)
    
    if not resp:
        return await q.edit("Invalid language")
    await message.reply_voice(resp)
    await q.edit("Done")

async def atts(text, tlang):
    gtts = gTTS(text, lang=tlang)
    bio = BytesIO()
    bio.name = "audio.mp3"
    try:
        gtts.write_to_fp(bio)
    except ValueError as e:
        return None
    return bio
