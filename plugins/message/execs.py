import asyncio
import html
import io
import os
import re
import traceback

from config import sudoers
from contextlib import redirect_stdout
from pyrogram import Client, filters

@Client.on_message(filters.su_cmd(r"(?P<cmd>ex(ec)?)\s+(?P<code>.+)", flags=re.S))
async def execs(client, message):
    lang = message.lang
    strio = io.StringIO()
    cmd = message.matches[0]['cmd']
    code = message.matches[0]['code']
    
    # Shortcuts that will be available for the user code
    reply = message.reply_to_message
    user = (reply or message).from_user
    chat = message.chat
    
    code_function = "async def __ex(client, message):"
    for line in code.split('\n'):
        code_function += f"\n    {line}"
    exec(code_function)
    
    with redirect_stdout(strio):
        try:
            await locals()["__ex"](client, message)
        except:
            traceback_string = traceback.format_exc()
            text = f'<b>{html.escape(traceback_string)}</b>'
            if cmd == 'ex':
                return await message.edit(text)
            return await message.reply(text)
    
    text = lang.executed_cmd
    output = strio.getvalue()
    if output:
        output = html.escape(output) # escape html special chars
        text = ''
        for line in output.splitlines():
            text += f"<code>{line}</code>\n"
        
        if cmd == 'ex':
            return await message.edit(text)
        await message.reply(text)