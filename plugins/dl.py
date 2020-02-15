from pyrogram import Client, Filters
from pySmartDL import SmartDL
from pyrogram.errors import MessageNotModified

import os
import time

last_edit = 0

@Client.on_message(Filters.command("dl", prefixes=".") & Filters.me)
async def download(client, message):
    await message.edit("Processing ...")
    if not message.reply_to_message:
        if '|' in message.text:
            url, name = message.text[4:].split('|')
        else:
            url = message.text[4:]
            name = message.text.split('/',--1)[1]
        dw1 = time.time()
        try:
            downloader = SmartDL(url, './dl/'+name, progress_bar=False)
            downloader.start(blocking=False)
        except Exception as e:
            await message.edit(f'an error has occurred: {e}')
            return
        await message.edit(f'downloading...')
        a = str(downloader.get_progress())[:3]
        while not downloader.isFinished():
            if a != str(downloader.get_progress())[:3]:
                    a = str(downloader.get_progress())[:3]
                    await message.edit(f'downloading... {a}')
        if downloader.isSuccessful():
            dw2 = time.time()
            up1 = time.time()
            a = f'Sending...'
            await message.edit(a)
            loc = downloader.get_dest()
            try:
                await client.send_document(message.chat.id, loc,caption=url, progress=progress, progress_args=(client, message, a))
            except Exception as e:
                await message.edit(f'an error has occurred: {e}')
                os.remove(loc.split('dl/',1)[1])
                return
            up2 = time.time()
            dw = round(dw2-dw1, 3)
            up = round(up2-up1, 3)
            to = round(up2-dw1, 3)
            await message.edit(f'Status:\nDownload: `{dw}`s\nUpload: `{up}`s\nTotal: `{to}`s')
            os.remove(loc.split('dl/',1)[1])

async def progress(current, total, c, m, a):
    global last_edit
    temp = current * 100 / total
    if last_edit + 3 < time.time():
        await c.send_chat_action(m.chat.id, 'UPLOAD_VIDEO')
        try:
            await m.edit(a + '\n' + "{:.1f}%".format(temp))
        except MessageNotModified:
            pass
        finally:
            last_edit = time.time()
