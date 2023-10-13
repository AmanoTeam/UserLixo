import html
import traceback

from pyrogram import Client, filters
from pyrogram.types import Message

from config import cmds
from utils import meval
import os


@Client.on_message(filters.command("eval", prefixes=".") & filters.me)
async def evals(client: Client, message: Message):
    text = message.text[6:]
    try:
        res = await meval(text, locals())
    except:
        ev = traceback.format_exc()
        await message.edit(ev)
        return
    else:
        try:
            if len(str(res)) > 4000:
                with open("output.txt", "w") as f:
                    f.write(str(res))
                await client.send_document(message.chat.id, "output.txt")
                os.remove("output.txt")
            else:
                await message.edit(f"<code>{html.escape(str(res))}</code>")
        except Exception as e:
            await message.edit(e)


cmds.update({".eval": "Run commands on eval"})
