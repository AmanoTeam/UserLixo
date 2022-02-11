import os
import re
import time

import chromeprinter
from pyrogram import Client, filters
from pyrogram.types import Message

from config import cmds

a = chromeprinter.Client()


@Client.on_message(filters.command("print", prefixes=".") & filters.me)
async def prints(client: Client, message: Message):
    url = message.text.split(" ", 1)[1]
    await message.edit(f"printing: {url}")
    ctime = time.time()
    if re.match(r"^[a-z]+://", url):
        url = url
    else:
        url = "http://" + url
    a.make_screenshot(url, f"{ctime}.png")
    try:
        await client.send_photo(message.chat.id, f"{ctime}.png")
    finally:
        os.remove(f"{ctime}.png")
    await message.delete()


cmds.update({".print": "Submit a print of a website"})
