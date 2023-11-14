import datetime
import io
import re
import shutil
import tempfile
from pathlib import Path

from pyrogram import Client, filters
from pyrogram.errors import BadRequest
from pyrogram.helpers import ikb
from pyrogram.types import CallbackQuery, Message
from yt_dlp import YoutubeDL
from utils import aiowrap, http, pretty_size
from config import bot, user

from locales import use_lang

YOUTUBE_REGEX = re.compile(
    r"(?m)http(?:s?):\/\/(?:www\.)?(?:music\.)?youtu(?:be\.com\/(watch\?v=|shorts/)|\.be\/|)([\w\-\_]*)(&(amp;)?[\w\?=]*)?"
)

TIME_REGEX = re.compile(r"[?&]t=([0-9]+)")

MAX_FILESIZE = 200000000


@aiowrap
def extract_info(instance: YoutubeDL, url: str, download=True):
    return instance.extract_info(url, download)


@Client.on_message(filters.command("ytdl", prefixes=".") & filters.sudoers)
@use_lang()
async def ytdlcmd(c: Client, m: Message, strings):
    user = m.from_user.id

    afsize = 0
    vfsize = 0

    if m.reply_to_message and m.reply_to_message.text:
        url = m.reply_to_message.text
    elif len(m.command) > 1:
        url = m.text.split(None, 1)[1]
    else:
        await m.reply(strings("ytdl_missing_argument"))
        return

    ydl = YoutubeDL({"noplaylist": True})

    match = YOUTUBE_REGEX.match(url)

    t = TIME_REGEX.search(url)
    temp = t.group(1) if t else 0

    if match:
        yt = await extract_info(ydl, match.group(), download=False)
    else:
        yt = await extract_info(ydl, f"ytsearch:{url}", download=False)
        yt = yt["entries"][0]

    for f in yt["formats"]:
        if f["format_id"] == "140" and f.get("filesize") is not None:
            afsize = f["filesize"] or 0
        if f["ext"] == "mp4" and f.get("filesize") is not None:
            vfsize = f["filesize"] or 0

    keyboard = [
        [
            (
                strings("ytdl_audio_button"),
                f'_aud.{yt["id"]}|{afsize}|{temp}|{m.chat.id}|{user}|{m.id}',
            ),
            (
                strings("ytdl_video_button"),
                f'_vid.{yt["id"]}|{vfsize}|{temp}|{m.chat.id}|{user}|{m.id}',
            ),
        ]
    ]

    if " - " in yt["title"]:
        performer, title = yt["title"].rsplit(" - ", 1)
    else:
        performer = yt.get("creator") or yt.get("uploader")
        title = yt["title"]

    text = f"🎧 <b>{performer}</b> - <i>{title}</i>\n"
    text += f"💾 <code>{pretty_size(afsize)}</code> (audio) / <code>{pretty_size(int(vfsize))}</code> (video)\n"
    text += f"⏳ <code>{datetime.timedelta(seconds=yt.get('duration'))}</code>"

    await m.reply(text, reply_markup=ikb(keyboard))


@bot.on_callback_query(filters.regex("^(_(vid|aud))") & filters.sudoers)
@use_lang()
async def cli_ytdl(c: Client, cq: CallbackQuery, strings):
    data, fsize, temp, cid, userid, mid = cq.data.split("|")
    if int(fsize) > MAX_FILESIZE:
        return await cq.answer(
            strings("ytdl_file_too_big"),
            show_alert=True,
            cache_time=60,
        )
    vid = re.sub(r"^\_(vid|aud)\.", "", data)
    url = f"https://www.youtube.com/watch?v={vid}"
    await cq.edit(strings("ytdl_downloading"))
    with tempfile.TemporaryDirectory() as tempdir:
        path = Path(tempdir) / "ytdl"

    ttemp = f"⏰ {datetime.timedelta(seconds=int(temp))} | " if int(temp) else ""
    if "vid" in data:
        ydl = YoutubeDL(
            {
                "outtmpl": f"{path}/%(title)s-%(id)s.%(ext)s",
                "format": "best[ext=mp4]",
                "max_filesize": MAX_FILESIZE,
                "noplaylist": True,
            }
        )
    else:
        ydl = YoutubeDL(
            {
                "outtmpl": f"{path}/%(title)s-%(id)s.%(ext)s",
                "format": "bestaudio[ext=m4a]",
                "max_filesize": MAX_FILESIZE,
                "noplaylist": True,
            }
        )
    try:
        yt = await extract_info(ydl, url, download=True)
    except BaseException as e:
        await cq.edit(strings("ytdl_send_error").format(errmsg=e))
        return
    await cq.edit(strings("ytdl_sending"))
    filename = ydl.prepare_filename(yt)
    thumb = io.BytesIO((await http.get(yt["thumbnail"])).content)
    thumb.name = "thumbnail.png"
    try:
        if "vid" in data:
            await user.send_video(
                int(cid),
                filename,
                width=1920,
                height=1080,
                caption=ttemp + yt["title"],
                duration=yt["duration"],
                thumb=thumb,
                reply_to_message_id=int(mid),
            )
        else:
            if " - " in yt["title"]:
                performer, title = yt["title"].rsplit(" - ", 1)
            else:
                performer = yt.get("creator") or yt.get("uploader")
                title = yt["title"]
            await user.send_audio(
                int(cid),
                filename,
                title=title,
                performer=performer,
                caption=ttemp[:-2],
                duration=yt["duration"],
                thumb=thumb,
                reply_to_message_id=int(mid),
            )
    except BadRequest as e:
        await cq.edit(strings("ytdl_send_error").format(errmsg=e))
    else:
        await cq.edit(strings("ytdl_sent"))

    shutil.rmtree(tempdir, ignore_errors=True)