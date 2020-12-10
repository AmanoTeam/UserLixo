import asyncio
import html
import io
import os
import re
import traceback

from userlixo.config import sudoers
from contextlib import redirect_stdout
from pyrogram import Client, filters

@Client.on_message(filters.su_cmd(r"(?P<cmd>ex(ec)?)\s+(?P<code>.+)", flags=re.S))
async def on_exec_user(c, m):
    await execs(c,m)

async def execs(c, m):
    lang = m._lang
    act = m.edit if await filters.me(c,m) else m.reply
    strio = io.StringIO()
    cmd = m.matches[0]['cmd']
    code = m.matches[0]['code']
    
    # Shortcuts that will be available for the user code
    reply = m.reply_to_message
    user = (reply or m).from_user
    chat = m.chat
    
    code_function = "async def __ex(c, m, reply, user, chat):"
    for line in code.split('\n'):
        code_function += f"\n    {line}"
    exec(code_function)
    
    with redirect_stdout(strio):
        try:
            await locals()["__ex"](c, m, reply, user, chat)
        except:
            traceback_string = traceback.format_exc()
            text = f'<b>{html.escape(traceback_string)}</b>'
            if cmd == 'exec':
                return await act(text)
            return await m.reply(text)
    
    text = lang.executed_cmd
    output = strio.getvalue()
    if output:
        if len(output) > 4096:
            with open('output.txt', 'w') as f:
                f.write(output)
            await m.reply_document('output.txt', quote=True)
            return os.remove('output.txt')
        output = html.escape(output) # escape html special chars
        text = ''
        for line in output.splitlines():
            text += f"<code>{line}</code>\n"
        
        if cmd == 'exec':
            return await act(text)
        await m.reply(text)