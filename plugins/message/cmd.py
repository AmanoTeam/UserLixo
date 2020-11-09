import asyncio
import html
import os
import re

from config import sudoers
from pyrogram import Client, filters
from utils import shell_exec

@Client.on_message(filters.su_cmd(r"(?P<command>cmd|sh)\s+(?P<code>.+)", flags=re.S))
async def cmd(client, message):
    lang = message.lang
    code = message.matches[0]['code']
    command = message.matches[0]['command']
    
    result, process = await shell_exec(code)
    output = result or lang.executed_cmd
    output = html.escape(output) # escape html special chars
    
    text = ''
    for line in output.splitlines():
        text += f"<code>{line}</code>\n"
    
    if command == 'cmd':
        return await message.edit(text)
    await message.reply(text)
