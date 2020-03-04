from pyrogram import Client, Filters

from config import cmds
from utils import meval
import traceback
import html

@Client.on_message(Filters.command("eval", prefixes=".") & Filters.me)
async def evals(client, message):
    text = message.text[6:]
    try:
        res = await meval(text, locals())
    except:
        ev = traceback.format_exc()
        await message.edit(ev)
        return
    else:
        try:
            await message.edit(f"<code>{html.escape(str(res))}</code>")
        except Exception as e:
            await message.edit(e)

cmds.update({'.eval':'Run commands on eval'})
