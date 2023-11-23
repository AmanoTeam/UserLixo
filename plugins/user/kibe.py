import asyncio
import math
import os
import time

import cv2
from PIL import Image
from pyrogram import Client, filters
from pyrogram.errors import ListenerTimeout, StickersetInvalid
from pyrogram.raw import functions, types
from pyrogram.raw.functions.messages import SendMedia
from pyrogram.raw.functions.stickers import AddStickerToSet, CreateStickerSet
from pyrogram.raw.types import (
    DocumentAttributeFilename,
    InputDocument,
    InputMediaUploadedDocument,
    InputStickerSetItem,
    InputStickerSetShortName,
)
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import bot, plugins, user
from db import Config, sticker
from locales import use_lang


@Client.on_message(filters.command("kibe", prefixes=".") & filters.sudoers)
@use_lang()
async def kibe(c: Client, m: Message, t):
    rmsg = m.reply_to_message
    emoji = None

    # Check if the command has an argument
    if len(m.text.split(" ")) > 1:
        emoji = m.text.split(" ")[1] 
    # Check if the replied message is a sticker
    elif rmsg and rmsg.sticker:
        emoji = rmsg.sticker.emoji

    # If no emoji, use the default or the one set in the settings
    if not emoji:
        settings = (await Config.get_or_create(id="kibe"))[0]
        if not settings.valuej:
            emoji = "🤔"
        else:
            emoji = settings.valuej["emoji"]
    
    # If the message was replied to, create the keyboard
    if rmsg:
        keyb = [
            [
                ("Sticker", f"kibes_{m.chat.id}_{rmsg.id}_{emoji}"),
                ("Emoji", f"kibee_{m.chat.id}_{rmsg.id}_{emoji}"),
            ], [
                ("Both", f"kibea_{m.chat.id}_{rmsg.id}_{emoji}"),
            ]
        ]

        await m.reply(t("kibe_choose"), reply_markup=keyb, reply_to_message_id=rmsg.id)

        # If the command was sent by the bot itself, delete the message
        if m.from_user.id == c.me.id:
            await m.delete()
    # If the message was not replied to, send an error message
    else:
        await m.edit(t("kibe_no_media"))


@bot.on_callback_query(filters.regex(r"^kibe") & filters.sudoers)
@use_lang()
async def kibe_callback(_, q: CallbackQuery, t):
    # Extract the chat ID, message ID, and emoji from the callback data
    cid, mid, emoji = q.data.split("_")[1:]
    # Get the original message
    msg = await user.get_messages(chat_id=cid, message_ids=int(mid))
    keyb = []
    # If the callback data starts with "kibes" or "kibea", create a sticker
    if q.data.startswith("kibes") or q.data.startswith("kibea"):
        res = await kibes(msg, q, t, emoji, issticker=True)
        keyb += [
                    InlineKeyboardButton(
                        text=t("kibes_open"),
                        url=f"t.me/addstickers/{res}",
                    )
                ]
    # If the callback data starts with "kibee" or "kibea", create an emoji
    if q.data.startswith("kibee") or q.data.startswith("kibea"):
        res = await kibes(msg, q, t, emoji, issticker=False)
        keyb += [
                    InlineKeyboardButton(
                        text=t("kibee_open"),
                        url=f"t.me/addemoji/{res}",
                    )
                ]

    # Edit the original message to indicate that the process is done
    await q.edit(t("kibe_done"), reply_markup=InlineKeyboardMarkup([keyb]))


async def kibes(rmessage: Message, q: CallbackQuery, t, emoji, issticker):
    # Inform the user that the process has started
    await q.edit(t("kibe_wait"))
    ctime = time.time()
    peer = await bot.resolve_peer(user.me.id)
    # Create the sticker packs if they don't exist
    if issticker:
        await sticker.get_or_create(type="photo")
        await sticker.get_or_create(type="animated")
        await sticker.get_or_create(type="video")
    else:
        await sticker.get_or_create(type="photoe")
        await sticker.get_or_create(type="animatede")
        await sticker.get_or_create(type="videoe")
    # If the bot doesn't have a username, use its first name
    if not user.me.username:
        user.me.username = user.me.first_name
    # Initialize variables to store the media type, file ID, and file extension
    media_type = None
    file_id = None
    file_extension = None
    # Check the type of the replied message and set the variables accordingly
    if rmessage.photo:
        media_type = "photo"
        file_id = rmessage.photo.file_id
        file_extension = ".png"
    elif rmessage.video:
        media_type = "video"
        file_id = rmessage.video.file_id
        file_extension = ".mp4"
    elif rmessage.animation:
        media_type = "video"
        file_id = rmessage.animation.file_id
        file_extension = ".mp4"
    elif rmessage.document:
        if "image" in rmessage.document.mime_type:
            media_type = "photo"
            file_id = rmessage.document.file_id
            file_extension = ".png"
        elif "video" in rmessage.document.mime_type:
            media_type = "video"
            file_id = rmessage.document.file_id
            file_extension = ".mp4"
    elif rmessage.sticker:
        if rmessage.sticker.is_animated:
            media_type = "animated"
            file_id = rmessage.sticker.file_id
            file_extension = ".tgs"
        elif rmessage.sticker.is_video:
            media_type = "video"
            file_id = rmessage.sticker.file_id
            file_extension = ".webm"
        else:
            media_type = "photo"
            file_id = rmessage.sticker.file_id
            file_extension = ".webp"

    # If the media type, file ID, and file extension are set, proceed with the process
    if media_type and file_id and file_extension:
        photo = await user.download_media(file_id, file_name=f"./{ctime}{file_extension}")
        packn = await sticker.get(type=media_type if issticker else f"{media_type}e")

    # Set the pack name and mime type based on the media type
    if media_type == "video":
        packname = "video"
        mime_type="video/webm"
        await q.edit(t("kibe_resize_video"))
        photo = await resize_video(photo, ctime, (512, 512) if issticker else (100, 100))
    elif media_type == "animated":
        mime_type="application/x-tgsticker"
        packname = "animated"
    else:
        await q.edit(t("kibe_resize_photo"))
        photo = await resize_photo(photo, ctime, (512, 512) if issticker else (100, 100))
        mime_type="image/png"
        packname = ""
    namp = "" if issticker else "_emoji"
    packnick = f"@{user.me.username}'s kibe {namp} pack V{packn.num}.0 {packname}"
    packname = f"a{user.me.id}{namp}_by_{user.me.username}_{packn.num}{('_'+packname) if packname else ''}_by_{bot.me.username}"
    try:
        stickerpack = await user.invoke(
            functions.messages.GetStickerSet(
                stickerset=types.InputStickerSetShortName(short_name=packname),
                hash=0,
            )
        )
    except StickersetInvalid:
        pack_exists = False
    else:
        pack_exists = True

    # If the pack exists and is full, create a new one
    if pack_exists and stickerpack.set.count > 119:
        packn.num += 1
        await sticker.get(type=packn.type).update(num=packn.num)
    ufile = await bot.save_file(photo)
    media = await bot.invoke(
        SendMedia(
            peer=peer,
            media=InputMediaUploadedDocument(
                file=ufile,
                mime_type=mime_type,
                attributes=[DocumentAttributeFilename(file_name=photo)],
            ),
            message="#Sticker kibe",
            random_id=bot.rnd_id(),
        )
    )
    for i in media.updates:
        if isinstance(i, types.UpdateNewMessage):
            stkr_file = i.message.media.document
            msg_id = i.message.id

    if pack_exists:
        # If the pack exists, add the sticker to it
        await q.edit(t("kibe_adding"))
        await bot.invoke(
            AddStickerToSet(
                stickerset=InputStickerSetShortName(short_name=packname),
                sticker=InputStickerSetItem(
                    document=InputDocument(
                        id=stkr_file.id,
                        access_hash=stkr_file.access_hash,
                        file_reference=stkr_file.file_reference,
                    ),
                    emoji=emoji,
                ),
            )
        )
    else:
        # If the pack doesn't exist, create it
        await q.edit(t("kibe_creating"))
        await bot.invoke(
                CreateStickerSet(
                    user_id=peer,
                    title=packnick,
                    short_name=packname,
                    stickers=[
                        InputStickerSetItem(
                            document=InputDocument(
                                id=stkr_file.id,
                                access_hash=stkr_file.access_hash,
                                file_reference=stkr_file.file_reference,
                            ),
                            emoji=emoji,
                        )
                    ],
                    animated=True if media_type == "animated" else False,
                    videos=True if media_type == "video" else False,
                    emojis=False if issticker else True,
                )
            )
    # Remove the downloaded file and delete the message from the bot's chat
    os.remove(photo)
    await bot.delete_messages(chat_id=user.me.id, message_ids=msg_id)

    return packname


async def resize_photo(photo, ctime, maxsize):
    """Resize the given photo to the specified max size"""
    image = Image.open(photo)
    # If the max size is 512 and both dimensions of the image are less than 512
    if maxsize[0] == 512 and ((image.width and image.height) < 512):
        size1 = image.width
        size2 = image.height
        # If the width is greater than the height
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
    # If the max size is 512 and either dimension of the image is greater than or equal to 512
    elif maxsize[0] == 512:
        image.thumbnail(maxsize)
    else:
        image.thumbnail(maxsize)
        # Create a new image with transparent background
        new_image = Image.new('RGBA', (100, 100), (0, 0, 0, 0))
        new_image.paste(image, (0, 0))
        image = new_image

    # Remove the original file
    os.remove(photo)

    # Save the resized image as a .webp file
    image.save(f"./{ctime}.webp", "webp")

    return f"./{ctime}.webp"


async def resize_video(video, ctime, maxsize):
    # Open the video file
    cap = cv2.VideoCapture(video)
    # If the max size is 512 and the width of the video is greater than or equal to the height
    if maxsize[1] == 512 and (cap.get(cv2.CAP_PROP_FRAME_WIDTH) >= cap.get(cv2.CAP_PROP_FRAME_HEIGHT)):
        scale = -1
    else:
        scale = maxsize[1]

    # Set the bitrate based on the max size
    if maxsize == (512, 512):
        file = "0.5M"
    else:
        file = "0.05M"

    # Define the command to resize the video using ffmpeg
    command = [
        "ffmpeg", "-i", video, "-vf", f"scale={maxsize[0]}:{scale}",
        "-c:v", "libvpx-vp9", "-b:v", file, "-r", "30", "-t", "3", "-an", f"n{ctime}.webm"
    ]

    # Run the command
    process = await asyncio.create_subprocess_exec(
        *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    await process.communicate()
    # Remove the original file
    os.remove(video)
    return f"./n{ctime}.webm"


plugins.append("kibe")


@bot.on_callback_query(filters.regex(r"\bconfig_plugin_kibe\b"))
async def config_kibe(c: Client, m: CallbackQuery):
    # Edit the message to display the settings for the "kibe" plugin
    await m.edit("Kibe settings", reply_markup=InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text="Emoji",
                callback_data="config_plugin_kibe_emoji"
            )
        ], [
            InlineKeyboardButton(
                text="Back",
                callback_data="config_plugins"
            )
        ]
    ]))


@bot.on_callback_query(filters.regex(r"config_plugin_kibe_emoji"))
async def config_kibe_emoji(c: Client, cq: CallbackQuery):
    # Get the settings for "kibe", or create them if they don't exist
    settings = (await Config.get_or_create(id="kibe"))[0]
    # If the settings are empty, initialize them with a default emoji
    if not settings.valuej:
        settings = {"emoji": "🤔"}
    else:
        settings = settings.valuej

    m = cq.message

    # Ask the user to send the emoji they want to use for "kibe"
    await cq.edit_message_text(f"Current emoji: {settings['emoji']}\nSend the emoji you want to use in kibe or /cancel to cancel")

    cmessage = None
    # Wait for the user to send a message with the new emoji
    while cmessage is None:
        try:
            cmessage = await m.chat.listen(filters.text & filters.sudoers)
        except ListenerTimeout:
            return

    text = cmessage.text

    # If the user sends "/cancel", cancel the operation and go back
    if text == "/cancel":
        return await cq.edit_message_text("Cancelled", reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    text="Back",
                    callback_data="config_plugin_kibe"
                )
            ]
        ]))

    # Update the settings with the new emoji
    settings["emoji"] = text
    await Config.get(id="kibe").update(valuej=settings)

    # Confirm to the user that the emoji has been set
    await cq.edit_message_text(f"Emoji set to {text}", reply_markup=InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text="Back",
                callback_data="config_plugin_kibe"
            )
        ]
    ]))
