import os
import time

import requests
import youtube_dl
from pyrogram import Client, Filters
from pyrogram.errors import MessageNotModified


@Client.on_message(Filters.command("ytdlv", prefixes=".") & Filters.me)
def ytdlv(client, message):
    url = message.text[7:]
    ydl = youtube_dl.YoutubeDL({'outtmpl': 'dls/%(title)s.%(ext)s', 'noplaylist': True})
    if 'youtu.be' not in url and 'youtube.com' not in url:
        yt = ydl.extract_info('ytsearch:' + url, download=False)['entries'][0]
        url = 'https://www.youtube.com/watch?v=' + yt['id']
    yt = ydl.extract_info(url, download=False)
    message.edit(f'Downloading `{yt["title"]}`')
    yt = ydl.extract_info(url, download=True)
    a = f'Sending `{yt["title"]}`'
    message.edit(a)
    ctime = time.time()
    r = requests.get(yt['thumbnail'])
    with open(f'{ctime}.png', 'wb') as f:
        f.write(r.content)
    client.send_video(message.chat.id, ydl.prepare_filename(yt), caption=yt["title"], duration=yt['duration'],
                      thumb=f'{ctime}.png', progress=progress, progress_args=(client, message, a))
    message.delete()
    os.remove(ydl.prepare_filename(yt))
    os.remove(f'{ctime}.png')


def progress(current, total, c, m, a):
    temp = current * 100 / total
    if '0' in "{:.1f}%".format(temp):
        c.send_chat_action(m.chat.id, 'UPLOAD_VIDEO')
        try:
            m.edit(a + '\n' + "{:.1f}%".format(temp))
        except MessageNotModified:
            pass
