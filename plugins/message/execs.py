import asyncio
import html
import io
import os
import re
import traceback

from config import sudoers
from contextlib import redirect_stdout
from pyrogram import Client, Filters

@Client.on_message(Filters.su_cmd(r"exec\s+(?P<code>.+)", flags=re.S))
async def execs(client, message):
    lang = message.lang
    strio = io.StringIO()
    code = message.matches[0]['code']
    
    # Shortcuts that will be available for the user code
    reply = message.reply_to_message
    user = (reply or message).from_user
    
    code_function = "async def __ex(client, message):"
    for line in code.split('\n'):
        code_function += f"\n    {line}"
    exec(code_function)
    
    with redirect_stdout(strio):
        try:
            await locals()["__ex"](client, message)
        except:
            traceback_string = traceback.format_exc()
            return await message.reply(f'<b>{html.escape(traceback_string)}</b>')
    
    text = lang.executed_cmd
    output = strio.getvalue()
    if output:
        output = html.escape(output) # escape html special chars
        text = ''
        for line in output.splitlines():
            text += f"<code>{line}</code>\n"
        
    await message.reply(text)