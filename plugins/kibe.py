import asyncio
import math
import os
import time

import cv2
from PIL import Image
from pyrogram import Client, filters
from pyrogram.errors import StickersetInvalid
from pyrogram.raw import functions, types
from pyrogram.types import Message

from config import cmds
from db import db, save


@Client.on_message(filters.command("kibe", prefixes=".") & filters.me)
async def kibe(client: Client, message: Message):
    emoji = message.text[6:]
    rsize, anim = False, False
    ctime = time.time()
    user = await client.get_me()
    packnames, packnicks = "", ""
    if not user.username:
        user.username = user.first_name
    if not "sticker" in db:
        db["sticker"] = {"photo": 1, "animated": 1, "video": 1}
        save(db)
    elif isinstance(db["sticker"], int):
        db["sticker"] = {
            "photo": db["sticker"],
            "animated": db["sticker"],
            "video": db["sticker"],
        }
        save(db)
    pack = db["sticker"]
    rmessage = message.reply_to_message
    if rmessage and rmessage.media:
        if rmessage.photo:
            photo = await client.download_media(
                rmessage.photo.file_id, file_name=f"./{ctime}.png"
            )
            rsize = True
            packn = pack["photo"]
        elif rmessage.video:
            photo = await client.download_media(
                rmessage.video.file_id, file_name=f"./{ctime}.mp4"
            )
            rsize = True
            anim = True
            packnames = "_video"
            packnicks = " video"
            packn = pack["video"]
        elif rmessage.document:
            photo = await client.download_media(
                rmessage.document.file_id, file_name=f"./{ctime}.png"
            )
            rsize = True
            packn = pack["photo"]
        elif rmessage.sticker:
            if len(emoji) == 0:
                emoji = rmessage.sticker.emoji
            if rmessage.sticker.is_animated:
                anim = True
                photo = await client.download_media(
                    rmessage.sticker.file_id, file_name=f"./{ctime}.tgs"
                )
                packnames = "_animated"
                packnicks = " animated"
                packn = pack["animated"]
            elif rmessage.sticker.is_video:
                anim = True
                photo = await client.download_media(
                    rmessage.sticker.file_id, file_name=f"./{ctime}.webm"
                )
                packnames = "_video"
                packnicks = " video"
                packn = pack["video"]
            else:
                anim = False
                photo = await client.download_media(
                    rmessage.sticker.file_id, file_name=f"./{ctime}.webp"
                )
                rsize = True
                packn = pack["photo"]

        packname = f"a{user.id}_by_{user.username}_{packn}{packnames}"
        packnick = f"@{user.username}'s kibe pack V{packn}.0{packnicks}"
        if not emoji:
            emoji = "👍"
        if rsize and not anim:
            photo = await resize_photo(photo, ctime)
        if rsize and anim:
            photo = await resize_video(photo, ctime)
        try:
            stickerpack = await client.invoke(
                functions.messages.GetStickerSet(
                    stickerset=types.InputStickerSetShortName(short_name=packname),
                    hash=0,
                )
            )
        except StickersetInvalid:
            pack_exists = False
        else:
            pack_exists = True
        # Get stickers chat id from username once
        stickers_chat = (await client.get_chat("stickers")).id
        if not pack_exists:
            await create_pack(
                message, client, stickers_chat, packnick, photo, emoji, packname
            )
        elif stickerpack.set.count > 119:
            if rmessage.photo or rmessage.document:
                db["sticker"]["photo"] += 1
                packn = db["sticker"]["photo"]
            elif rmessage.sticker.is_animated:
                db["sticker"]["animated"] += 1
                packnames = "_animated"
                packnicks = " animated"
                packn = db["sticker"]["animated"]
            elif rmessage.sticker.is_video or rmessage.video:
                db["sticker"]["video"] += 1
                packnames = "_video"
                packnicks = " video"
                packn = db["sticker"]["video"]
            else:
                db["sticker"]["photo"] += 1
                packn = db["sticker"]["photo"]
            save(db)
            packname = f"a{user.id}_by_{user.username}_{packn}{packnames}"
            packnick = f"@{user.username}'s kibe pack V{packn}.0{packnicks}"
            await create_pack(
                message, client, stickers_chat, packnick, photo, emoji, packname
            )
        else:
            # Add a new sticker
            await asyncio.gather(
                client.wait_for_message(stickers_chat, timeout=30),
                client.send_message(stickers_chat, "/addsticker"),
            )
            # Define pack name
            await asyncio.gather(
                client.wait_for_message(stickers_chat, timeout=30),
                client.send_message(stickers_chat, packname),
            )
            # Send sticker image
            await asyncio.gather(
                client.wait_for_message(stickers_chat, timeout=30),
                client.send_document(stickers_chat, photo),
            )
            # Send sticker emoji
            await asyncio.gather(
                client.wait_for_message(stickers_chat, timeout=30),
                client.send_message(stickers_chat, emoji),
            )
            # We are done
            await client.send_message(stickers_chat, "/done")
            await message.edit(f"[kibed](http://t.me/addstickers/{packname})")
            os.remove(photo)


async def resize_photo(photo, ctime):
    """Resize the given photo to 512x512"""
    image = Image.open(photo)
    maxsize = (512, 512)
    if (image.width and image.height) < 512:
        size1 = image.width
        size2 = image.height
        if image.width > image.height:
            scale = 512 / size1
            size1new = 512
            size2new = size2 * scale
        else:
            scale = 512 / size2
            size1new = size1 * scale
            size2new = 512
        size1new = math.floor(size1new)
        size2new = math.floor(size2new)
        sizenew = (size1new, size2new)
        image = image.resize(sizenew)
    else:
        image.thumbnail(maxsize)

    os.remove(photo)

    image.save(f"./{ctime}.webp", "webp")

    return f"./{ctime}.webp"

async def resize_video(video, ctime):
    cap = cv2.VideoCapture(video)
    if cap.get(cv2.CAP_PROP_FRAME_WIDTH) >= cap.get(cv2.CAP_PROP_FRAME_HEIGHT):
        scale = -1
    else:
        scale = 512

    command = [
        "ffmpeg", "-i", video, "-vf", f"scale=512:{scale}",
        "-c:v", "libvpx-vp9", "-b:v", "0.5M", "-r", "30", "-t", "3", "-an", f"{ctime}.webm"
    ]

    process = await asyncio.create_subprocess_exec(
        *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    await process.communicate()
    os.remove(video)
    return f"./{ctime}.webm"

async def create_pack(
    message: Message,
    client: Client,
    stickers_chat: int,
    packnick: str,
    photo: str,
    emoji: str,
    packname: str,
):
    await message.edit("criando novo pack")
    # Create pack
    rmessage = message.reply_to_message
    if rmessage.sticker:
        if rmessage.sticker.is_video:
            await client.send_message(stickers_chat, "/newvideo")
        elif rmessage.sticker.is_animated:
            await client.send_message(stickers_chat, "/newanimated")
        else:
            await client.send_message(stickers_chat, "/newpack")
    else:
        await client.send_message(stickers_chat, "/newpack")

    # Set a name for it
    await asyncio.gather(
        client.wait_for_message(stickers_chat, timeout=30),
        client.send_message(stickers_chat, packnick),
    )
    # Send the first sticker of the pack
    await asyncio.gather(
        client.wait_for_message(stickers_chat, timeout=30),
        client.send_document(stickers_chat, photo),
    )
    # Sleep for a bit
    await asyncio.sleep(1.5)
    # Send the emoji for the first sticker
    await asyncio.gather(
        client.wait_for_message(stickers_chat, timeout=30),
        client.send_message(stickers_chat, emoji),
    )
    # Publish the sticker pack
    res = await asyncio.gather(
        client.wait_for_message(stickers_chat, timeout=30),
        client.send_message(stickers_chat, "/publish"),
    )
    if res[0].text == "Choose the sticker set you want to publish.":
        # Send the sticker pack name
        await asyncio.gather(
            client.wait_for_message(stickers_chat, timeout=30),
            client.send_message(stickers_chat, "<" + packnick + ">"),
        )
    # Skip setting sticker pack icon
    await asyncio.gather(
        client.wait_for_message(stickers_chat, timeout=30),
        client.send_message(stickers_chat, "/skip"),
    )
    # Set sticker pack url
    await asyncio.gather(
        client.wait_for_message(stickers_chat, timeout=30),
        client.send_message(stickers_chat, packname),
    )
    await message.edit(f"[kibed](http://t.me/addstickers/{packname})")
    os.remove(photo)


cmds.update({".kibe": "Kibe a image, video or sticker"})
