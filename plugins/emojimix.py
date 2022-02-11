import asyncio
import os
import time

from pyrogram import Client, filters
from pyrogram.types import Message

from plugins.kibe import resize_photo
from utils import http

versions = [
    "20201001",
    "20210218",
    "20210521",
    "20210831",
    "20211115",
    "20220110",
]


emoji = lambda x: "-".join(f"u{ord(i):x}" for i in x)


@Client.on_message(filters.command("emojimix", prefixes=".") & filters.me)
async def emojimix(client: Client, message: Message):
    text = message.text.split(" ", 1)[1].split("+")
    emoji1, emoji2 = emoji(text[0]), emoji(text[1])
    ctime = time.time()

    tasks = []
    # get all versions with async gather
    for version in versions:
        tasks.append(
            http.get(
                f"https://www.gstatic.com/android/keyboard/emojikitchen/{version}/{emoji1}/{emoji1}_{emoji2}.png"
            )
        )
        tasks.append(
            http.get(
                f"https://www.gstatic.com/android/keyboard/emojikitchen/{version}/{emoji2}/{emoji2}_{emoji1}.png"
            )
        )
    # Reverse the order of the tasks, so that the first successful response is from the newest version
    tasks.reverse()
    responses = await asyncio.gather(*tasks)
    image = None
    for response in responses:
        if response.status_code == 200:
            image = response.url
            break
    if not image:
        await message.edit("These emojis cannot be combined.")
        return
    r = await http.get(image)
    with open(f"{ctime}.png", "wb") as f:
        f.write(r.read())
    photo = await resize_photo(f"{ctime}.png", ctime)
    await message.delete()
    await client.send_document(
        message.chat.id,
        photo,
        reply_to_message_id=None
        if not message.reply_to_message
        else message.reply_to_message.message_id,
    )
    os.remove(photo)
