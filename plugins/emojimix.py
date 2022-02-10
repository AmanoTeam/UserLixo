from config import cmds
from plugins.kibe import resize_photo
import httpx
import time
import os

from pyrogram import Client, filters

def emoji(x):
    txt = x.encode("unicode-escape").decode()
    res = ""
    for i in txt.locate("\\"):
        if "U" in i:
            i = 'u'+i[5:]
        res += i+"-"
    return res[:-1]

@Client.on_message(filters.command("emojimix", prefixes='.') & filters.me)
async def emojimix(client, message):
    text = message.text.split(" ",1)[1]
    emoji1, emoji2 = emoji(text[0]), emoji(text[1])
    ctime = time.time()
    async with httpx.AsyncClient() as session:
        im1 = f"https://www.gstatic.com/android/keyboard/emojikitchen/20201001/{emoji1}/{emoji1}_{emoji2}.png"
        im2 = f"https://www.gstatic.com/android/keyboard/emojikitchen/20201001/{emoji2}/{emoji2}_{emoji1}.png"
        if (await session.head(im1)).headers.get("content-type") == "image/png":
            im = im1
        elif (await session.head(im2)).headers.get("content-type") == "image/png":
            im = im2
        else:
            await message.edit("These emojis cannot be combined.")
            return
        r = await session.get(im)
        with open(f'{ctime}.png', 'wb') as f:
            f.write(r.read())
    photo = await resize_photo(f'{ctime}.png', ctime)
    await message.delete()
    await client.send_document(message.chat.id, photo)
    os.remove(photo)
