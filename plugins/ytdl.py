import os
import time
from functools import partial

import aiohttp
import youtube_dl
from pyrogram import Client, filters
from pyrogram.errors import MessageNotModified
from pyrogram.types import Message

from config import cmds
from utils import aiowrap

last_edit = 0


@aiowrap
def extract_info(instance, url, download=True):
    return instance.extract_info(url, download)


@Client.on_message(filters.command("ytdl", prefixes=".") & filters.me)
async def ytdl(client: Client, message: Message):
    url = message.text.split(maxsplit=1)[1]
    if "-m4a" in url:
        url = url.replace(" -m4a", "")
        ydl = youtube_dl.YoutubeDL(
            {
                "outtmpl": "dls/%(title)s-%(id)s.%(ext)s",
                "format": "140",
                "noplaylist": True,
            }
        )
        vid = False
    else:
        url = url.replace(" -mp4", "")
        ydl = youtube_dl.YoutubeDL(
            {
                "outtmpl": "dls/%(title)s-%(id)s.%(ext)s",
                "format": "mp4",
                "noplaylist": True,
            }
        )
        vid = True
    if "youtu.be" not in url and "youtube.com" not in url:
        yt = await extract_info(ydl, "ytsearch:" + url, download=False)
        yt = yt["entries"][0]
        url = "https://www.youtube.com/watch?v=" + yt["id"]
    else:
        yt = await extract_info(ydl, url, download=False)
        url = "https://www.youtube.com/watch?v=" + yt["id"]
    a = f'Downloading `{yt["title"]}`'
    await message.edit(a)

    progress_hook = partial(ydl_progress, client, message, a)
    ydl.add_progress_hook(progress_hook)
    yt = await extract_info(ydl, url, download=True)
    a = f'Sending `{yt["title"]}`'
    await message.edit(a)
    ctime = time.time()
    async with aiohttp.ClientSession() as session:
        r = await session.get(yt["thumbnail"])
        with open(f"{ctime}.png", "wb") as f:
            f.write(await r.read())

    filename = ydl.prepare_filename(yt)

    if vid:
        await client.send_video(
            message.chat.id,
            filename,
            width=int(1920),
            height=int(1080),
            caption=yt["title"],
            duration=yt["duration"],
            thumb=f"{ctime}.png",
            progress=progress,
            progress_args=(client, message, a),
        )
    else:
        if " - " in yt["title"]:
            performer, title = yt["title"].rsplit(" - ", 1)
        else:
            performer = yt.get("creator") or yt.get("uploader")
            title = yt["title"]
        await client.send_audio(
            message.chat.id,
            filename,
            title=title,
            performer=performer,
            duration=yt["duration"],
            thumb=f"{ctime}.png",
            progress=progress,
            progress_args=(client, message, a),
        )

    await message.delete()
    os.remove(filename)
    os.remove(f"{ctime}.png")


async def progress(current, total, c, m, a):
    global last_edit
    percent = current * 100 / total
    if last_edit + 1 < int(time.time()) or current == total:
        await c.send_chat_action(m.chat.id, "UPLOAD_VIDEO")
        try:
            await m.edit(a + "\n" + "{:.1f}%".format(percent))
        except MessageNotModified:
            pass
        finally:
            last_edit = int(time.time())


def ydl_progress(c, m, a, status):
    global last_edit
    if status["status"] == "finished":
        return
    percent = status["_percent_str"]
    if last_edit + 1 < int(time.time()):
        try:
            m.edit_text(f"{a}\n{percent}")
        except MessageNotModified:
            pass
        finally:
            last_edit = int(time.time())


cmds.update({".ytdl": "Download a youtube video"})
