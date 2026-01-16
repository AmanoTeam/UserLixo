import datetime
import io
import os
import re
import tempfile
from pathlib import Path

from hydrogram import Client, filters
from hydrogram.errors import BadRequest
from hydrogram.helpers import ikb
from hydrogram.types import CallbackQuery, Message
from yt_dlp import YoutubeDL

from config import bot, user
from locales import use_lang
from utils import aiowrap, http, pretty_size

# --- CONFIGURAÇÃO ---
# Agora os cookies ficam na pasta data/
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)  # Cria a pasta se não existir
COOKIES_FILE = DATA_DIR / "ytdl-cookies.txt"
MAX_FILESIZE = 2000 * 1024 * 1024  # 2GB

YOUTUBE_REGEX = re.compile(
    r"(?m)http(?:s?):\/\/(?:www\.)?(?:music\.)?youtu(?:be\.com\/(watch\?v=|shorts/)|\.be\/|)([\w\-\_]*)(&(amp;)?[\w\?=]*)?"
)
TIME_REGEX = re.compile(r"[?&]t=([0-9]+)")

@aiowrap
def extract_info(instance: YoutubeDL, url: str, download=True):
    return instance.extract_info(url, download)

@Client.on_message(filters.command("ytdl", prefixes=".") & filters.sudoers)
@use_lang()
async def ytdlcmd(c: Client, m: Message, strings):
    user_id = m.from_user.id
    afsize, vfsize = 0, 0

    if m.reply_to_message and m.reply_to_message.text:
        url = m.reply_to_message.text
    elif len(m.command) > 1:
        url = m.text.split(None, 1)[1]
    else:
        await m.reply(strings("ytdl_missing_argument"))
        return

    ydl_opts = {
        "noplaylist": True, 
        "quiet": True,
        "no_warnings": True,
    }
    # Verifica se o arquivo de cookies existe na pasta data/
    if COOKIES_FILE.exists():
        ydl_opts["cookiefile"] = str(COOKIES_FILE)
        print(f"[YTDL] Usando cookies de: {COOKIES_FILE}")

    ydl = YoutubeDL(ydl_opts)
    match = YOUTUBE_REGEX.match(url)
    t = TIME_REGEX.search(url)
    temp = t.group(1) if t else 0

    try:
        if match:
            yt = await extract_info(ydl, match.group(), download=False)
        else:
            yt = await extract_info(ydl, f"ytsearch1:{url}", download=False)
            yt = yt["entries"][0]
    except Exception as e:
        clean_err = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', str(e))
        await m.reply(strings("ytdl_search_error").format(error=clean_err[:500]))
        return

    # --- NOVA LÓGICA DE TAMANHO ROBUSTA ---
    formats = yt.get("formats", [])
    
    # Pegar o maior áudio disponível (independente de ser m4a ou webm)
    audio_formats = [f for f in formats if f.get('vcodec') == 'none']
    if audio_formats:
        # Ordena pelo tamanho para pegar o maior (melhor qualidade)
        audio_formats.sort(key=lambda x: x.get('filesize') or x.get('filesize_approx') or 0)
        best_a = audio_formats[-1]
        afsize = best_a.get('filesize') or best_a.get('filesize_approx') or 0

    # Pegar o maior vídeo disponível
    video_formats = [f for f in formats if f.get('vcodec') != 'none']
    if video_formats:
        video_formats.sort(key=lambda x: x.get('filesize') or x.get('filesize_approx') or 0)
        best_v = video_formats[-1]
        v_raw = best_v.get('filesize') or best_v.get('filesize_approx') or 0
        # No YouTube, vídeos HD são DASH (vídeo e áudio separados), então somamos
        vfsize = v_raw + afsize

    keyboard = [
        [
            (strings("ytdl_audio_button"), f'_aud.{yt["id"]}|{afsize}|{temp}|{m.chat.id}|{user_id}|{m.id}'),
            (strings("ytdl_video_button"), f'_vid.{yt["id"]}|{vfsize}|{temp}|{m.chat.id}|{user_id}|{m.id}'),
        ]
    ]

    performer = yt.get("uploader", "YouTube")
    title = yt.get("title", "Video")
    text = f"🎧 <b>{performer}</b> - <i>{title}</i>\n"
    text += f"💾 <code>{pretty_size(afsize)}</code> (audio) / <code>{pretty_size(int(vfsize))}</code> (video)\n"
    text += f"⏳ <code>{datetime.timedelta(seconds=yt.get('duration', 0))}</code>"

    await m.reply(text, reply_markup=ikb(keyboard))

@bot.on_callback_query(filters.regex("^(_(vid|aud))") & filters.sudoers)
@use_lang()
async def cli_ytdl(c: Client, cq: CallbackQuery, strings):
    try:
        data, fsize, temp, cid, userid, mid = cq.data.split("|")
    except: 
        return await cq.answer(strings("ytdl_missing_argument"))

    if fsize and int(fsize) > MAX_FILESIZE:
        return await cq.answer(strings("ytdl_file_too_big").format(size=pretty_size(MAX_FILESIZE)), show_alert=True) 

    vid_id = re.sub(r"^\_(vid|aud)\.", "", data)
    url = f"https://www.youtube.com/watch?v={vid_id}"
    await cq.edit_message_text(strings("ytdl_downloading"))

    with tempfile.TemporaryDirectory() as tempdir:
        path = Path(tempdir)
        
        opts = {
            "outtmpl": f"{path}/%(title)s-%(id)s.%(ext)s",
            "noplaylist": True,
            "quiet": True,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
        # Verifica se o arquivo de cookies existe na pasta data/
        if COOKIES_FILE.exists():
            opts["cookiefile"] = str(COOKIES_FILE)
            print(f"[YTDL-DOWNLOAD] Usando cookies de: {COOKIES_FILE}")

        # --- SELETORES DE FORMATO CORRIGIDOS ---
        if "vid" in data:
            # Busca o melhor vídeo mp4 e o melhor áudio m4a e junta eles. Se não der, pega o melhor mp4 geral.
            opts["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        else:
            # FORÇA apenas áudio. Se não houver m4a, ele baixa webm e o ffmpeg converte (se instalado).
            opts["format"] = "bestaudio[ext=m4a]/bestaudio/best"
            # Adicionamos uma instrução para converter para áudio caso ele baixe um vídeo por engano
            opts["postprocessors"] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
                'preferredquality': '192',
            }]

        ydl = YoutubeDL(opts)
        try:
            yt = await extract_info(ydl, url, download=True)
        except Exception as e:
            clean_err = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', str(e))
            return await cq.edit_message_text(f"❌ Erro: {clean_err[:500]}")

        await cq.edit_message_text(strings("ytdl_sending"))
        filename = ydl.prepare_filename(yt)
        
        # O post-processor do áudio muda a extensão para .m4a
        if "aud" in data:
            filename = os.path.splitext(filename)[0] + ".m4a"

        # Verificação extra se o arquivo existe (as vezes extensões mudam)
        if not os.path.exists(filename):
            base = os.path.splitext(filename)[0]
            for ext in ['.mp4', '.mkv', '.webm', '.m4a', '.mp3']:
                if os.path.exists(base + ext):
                    filename = base + ext
                    break

        try:
            if "vid" in data:
                await user.send_video(
                    chat_id=int(cid), 
                    video=filename, 
                    caption=yt.get("title"), 
                    duration=yt.get("duration", 0), 
                    reply_to_message_id=int(mid)
                )
            else:
                await user.send_audio(
                    chat_id=int(cid), 
                    audio=filename, 
                    title=yt.get("title"), 
                    performer=yt.get("uploader"), 
                    duration=yt.get("duration", 0), 
                    reply_to_message_id=int(mid)
                )
        except Exception as e:
            await cq.edit_message_text(strings("ytdl_send_error").format(e=e))
        else:
            await cq.edit_message_text(strings("ytdl_sent"))
