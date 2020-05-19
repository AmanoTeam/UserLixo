import os
import time

import aiohttp
import youtube_dl
from config import cmds
from utils import aiowrap
from pyrogram import Client, Filters
from pyrogram.errors import MessageNotModified

last_edit = 0


@aiowrap
def extract_info(instance, url, download=True):
    return instance.extract_info(url, download)


@Client.on_message(Filters.command("ytdl", prefixes=".") & Filters.me)
async def ytdl(client, message):
    url = message.text.split(' ',1)[1]
    if '-m4a' in url:
        url = url.replace(' -m4a','')
        ydl = youtube_dl.YoutubeDL({'outtmpl': 'dls/%(title)s-%(id)s.%(ext)s', 'format': '140', 'noplaylist': True})
        vid = False
    else:
        url = url.replace(' -mp4','')
        ydl = youtube_dl.YoutubeDL({'outtmpl': 'dls/%(title)s-%(id)s.%(ext)s', 'format': 'mp4', 'noplaylist': True})
        vid = True
    if 'youtu.be' not in url and 'youtube.com' not in url:
        yt = await extract_info(ydl, 'ytsearch:' + url, download=False)
        yt = yt['entries'][0]
        url = 'https://www.youtube.com/watch?v=' + yt['id']
    else:
        yt = await extract_info(ydl, url, download=False)
        url = 'https://www.youtube.com/watch?v=' + yt['id']
    await message.edit(f'Downloading `{yt["title"]}`')
    yt = await extract_info(ydl, url, download=True)
    a = f'Sending `{yt["title"]}`'
    await message.edit(a)
    ctime = time.time()
    async with aiohttp.ClientSession() as session:
        r = await session.get(yt['thumbnail'])
        with open(f'{ctime}.png', 'wb') as f:
            f.write(await r.read())
    # Workaround for when youtube-dl changes file extension without telling us.
    filename = ydl.prepare_filename(yt)


    if vid:
        await client.send_video(message.chat.id, filename, width=int(1920), height=int(1080), caption=yt["title"], duration=yt['duration'],
                          thumb=f'{ctime}.png', progress=progress, progress_args=(client, message, a))
    else:
        if ' - ' in yt["title"]:
            performer, title = yt["title"].rsplit(' - ', 1)
        else:
            performer = yt.get('creator') or yt.get('uploader')
            title = yt["title"]
        await client.send_audio(message.chat.id, filename,  title=title, performer=performer, duration=yt['duration'],
                          thumb=f'{ctime}.png', progress=progress, progress_args=(client, message, a))

    await message.delete()
    os.remove(filename)
    os.remove(f'{ctime}.png')


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

cmds.update({'.ytdl':'Download a youtube video'})
