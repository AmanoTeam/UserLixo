import asyncio
import html
import os
import re

from config import sudoers
from pyrogram import Client, filters

@Client.on_message(filters.su_cmd(r"cmd\s+(?P<code>.+)", flags=re.S))
async def cmd(client, message):
    lang = message.lang
    code = message.matches[0]['code']
    process = await asyncio.create_subprocess_shell(
        code,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT)
    result = await process.communicate()
    output = result[0].decode().rstrip() or lang.executed_cmd
    output = html.escape(output) # escape html special chars
    text = ''
    for line in output.splitlines():
        text += f"<code>{line}</code>\n"
    await message.reply(text)
