import html

from pyrogram import Client, filters
from pyrogram.types import Message

from config import cmds


@Client.on_message(filters.command("help", prefixes=".") & filters.me)
async def chelp(client: Client, message: Message):
    if message.text[6:]:
        a = message.text[6:]
        if a in cmds:
            await message.edit(f"<code>{html.escape(a)}</code>: {cmds[a]}")
        else:
            await message.edit(f"Command '<code>{html.escape(a)}</code>' not found.")

    else:
        a = ["<code>{}</code>: {}".format(html.escape(i), cmds[i]) for i in cmds]
        await message.edit("\n".join(a))


cmds.update({".help": "List all the commands"})
