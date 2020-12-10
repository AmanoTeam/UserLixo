import asyncio
import html
import os
import re

from userlixo.config import sudoers
from pyrogram import Client, filters
from userlixo.utils import shell_exec

@Client.on_message(filters.su_cmd(r"(?P<command>cmd|sh)\s+(?P<code>.+)", flags=re.S))
async def on_cmd_user(c, m):
    await cmd(c,m)

async def cmd(c, m):
    lang = m._lang
    act = m.edit if await filters.me(c,m) else m.reply
    
    code = m.matches[0]['code']
    command = m.matches[0]['command']
    
    result, process = await shell_exec(code)
    output = result or lang.executed_cmd
    
    if len(output) > 4096:
        with open('output.txt', 'w') as f:
            f.write(output)
        await m.reply_document('output.txt', quote=True)
        return os.remove('output.txt')
    
    output = html.escape(output) # escape html special chars
    
    text = ''
    for line in output.splitlines():
        text += f"<code>{line}</code>\n"
    
    if command == 'cmd':
        return await act(text)
    await m.reply(text)
