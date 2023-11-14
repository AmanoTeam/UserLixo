import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message
from locales import use_lang

@Client.on_message(filters.command("cmd", prefixes=".") & filters.sudoers)
@use_lang()
async def cmd(_, m: Message, t):
    text = m.text[5:]
    proc = await asyncio.create_subprocess_shell(
        text, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
    )
    ex = await proc.communicate()
    res = ex[0].decode().rstrip() or t("cmd_no_output")
    await m.edit(res)
