import asyncio
import math
import os
import time

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
    rsize = False
    ctime = time.time()
    user = await client.get_me()
    if not user.username:
        user.username = user.first_name
    if "sticker" in db:
        pack = db["sticker"]
    else:
        pack = 1
    packname = f"a{user.id}_by_{user.username}_{pack}"
    packnick = f"@{user.username}'s kibe pack V{pack}.0"
    rmessage = message.reply_to_message
    if rmessage and rmessage.media:
        if rmessage.photo:
            photo = await client.download_media(
                rmessage.photo.file_id, file_name=f"./{ctime}.png"
            )
            rsize = True
        elif rmessage.document:
            photo = await client.download_media(
                rmessage.document.file_id, file_name=f"./{ctime}.png"
            )
            rsize = True
        elif rmessage.sticker:
            if len(emoji) == 0:
                emoji = rmessage.sticker.emoji
            if rmessage.sticker.is_animated:
                anim = True
                photo = await client.download_media(
                    rmessage.sticker.file_id, file_name=f"./{ctime}.tgs"
                )
                packname += "_animated"
                packnick += " animated"
            else:
                anim = False
                photo = await client.download_media(
                    rmessage.sticker.file_id, file_name=f"./{ctime}.webp"
                )
                rsize = True
        if not emoji:
            emoji = "👍"
        if rsize:
            photo = await resize_photo(photo, ctime)
        try:
            stickerpack = await client.send(
                functions.messages.GetStickerSet(
                    stickerset=types.InputStickerSetShortName(short_name=packname),
                    hash=0,
                )
            )
        except StickersetInvalid:
            pack_exists = False
        else:
            pack_exists = True
        stickers_chat = "Stickers"
        if not pack_exists:
            await create_pack(
                anim, message, client, stickers_chat, packnick, photo, emoji, packname
            )
        elif stickerpack.set.count > 119:
            pack += 1
            db["sticker"] = pack
            save(db)
            packname = f"a{user.id}_by_{user.username}_{pack}"
            await create_pack(
                anim, message, client, stickers_chat, packnick, photo, emoji, packname
            )
        else:
            # Add a new sticker
            await asyncio.gather(
                client.send_message(stickers_chat, "/addsticker"),
                client.wait_for_message(stickers_chat, timeout=30),
            )
            # Define pack name
            await asyncio.gather(
                client.send_message(stickers_chat, packname),
                client.wait_for_message(stickers_chat, timeout=30),
            )
            # Send sticker image
            await client.send_document(stickers_chat, photo)
            time.sleep(0.8)
            # Send sticker emoji
            await asyncio.gather(
                client.send_message(stickers_chat, emoji),
                client.wait_for_message(stickers_chat, timeout=30),
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

    image.convert("RGB")
    image.save(f"./{ctime}.webp", "webp")

    return f"./{ctime}.webp"


async def create_pack(anim, message, client, st, packnick, photo, emoji, packname):
    await message.edit("criando novo pack")
    # Create pack
    if not anim:
        await client.send_message(st, "/newpack")
    else:
        await client.send_message(st, "/newanimated")
    # Set a name for it
    await client.send_message(st, packnick)
    # Send the first sticker of the pack
    await client.send_document(st, photo)
    # Send the emoji for the first sticker
    await client.send_message(st, emoji)
    time.sleep(0.8)
    # Publish the sticker pack
    await client.send_message(st, "/publish")
    if anim:
        await client.send_message(st, "<" + packnick + ">")
    # Skip setting sticker pack icon
    await client.send_message(st, "/skip")
    # Set sticker pack url
    await client.send_message(st, packname)
    await message.edit(f"[kibed](http://t.me/addstickers/{packname})")
    os.remove(photo)


cmds.update({".kibe": "Kibe a image or sticker"})
