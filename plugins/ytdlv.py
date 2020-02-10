import os
import time
from glob import glob

import requests
import youtube_dl
from pyrogram import Client, Filters
from pyrogram.errors import MessageNotModified

last_edit = 0


@Client.on_message(Filters.command("ytdlv", prefixes=".") & Filters.me)
async def ytdlv(client, message):
    url = message.text[7:]
    if '-m4a' in url:
        url = url.replace(' -m4a','')
        ydl = youtube_dl.YoutubeDL({'outtmpl': 'dls/%(title)s-%(id)s.%(ext)s', 'format': '140', 'noplaylist': True})
        vid = False
    else:
        url = url.replace(' -mp4','')
        ydl = youtube_dl.YoutubeDL({'outtmpl': 'dls/%(title)s-%(id)s.%(ext)s', 'noplaylist': True})
        vid = True
    if 'youtu.be' not in url and 'youtube.com' not in url:
        yt = ydl.extract_info('ytsearch:' + url, download=False)['entries'][0]
        url = 'https://www.youtube.com/watch?v=' + yt['id']
    else:
        yt = ydl.extract_info(url, download=False)
        url = 'https://www.youtube.com/watch?v=' + yt['id']
    await message.edit(f'Downloading `{yt["title"]}`')
    yt = ydl.extract_info(url, download=True)
    a = f'Sending `{yt["title"]}`'
    await message.edit(a)
    ctime = time.time()
    r = requests.get(yt['thumbnail'])
    with open(f'{ctime}.png', 'wb') as f:
        f.write(r.content)
    # Workaround for when youtube-dl changes file extension without telling us.
    filename = ydl.prepare_filename(yt).rsplit(".", 1)[0]
    filename = glob(f"{filename}.*")[0]
    
    if vid:
        await client.send_video(message.chat.id, filename, caption=yt["title"], duration=yt['duration'],
                          thumb=f'{ctime}.png', progress=progress, progress_args=(client, message, a))
    else:
        if ' - ' in yt["title"]:
            performer, title = yt["title"].rsplit(' - ', 1)
        else:
            performer = yt.get('creator') or yt.get('uploader')
            title = yt["title"]
        await client.send_audio(message.chat.id, filename, title=title, performer=performer, duration=yt['duration'],
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
