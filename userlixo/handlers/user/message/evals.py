import asyncio
import html
import os
import re
import traceback

from userlixo.config import sudoers
from pyrogram import Client, filters
from meval import meval

@Client.on_message(filters.su_cmd(r"(?P<cmd>ev(al)?)\s+(?P<code>.+)", flags=re.S))
async def evals(c, m):
    act = m.edit if await filters.me(c,m) else m.reply
    cmd = m.matches[0]['cmd']
    eval_code = m.matches[0]['code']
    
    # Shortcuts that will be available for the user code
    reply = m.reply_to_message
    user = (reply or m).from_user
    chat = m.chat
    
    try:
        output = await meval(eval_code, globals(), **locals())
    except:
        traceback_string = traceback.format_exc()
        text = f"Exception while running the code:\n{traceback_string}"
        if cmd == 'eval':
            return await act(text)
        return await m.reply(text)
    else:
        try:
            output = html.escape(str(output)) # escape html special chars
            text = ''
            for line in output.splitlines():
                text += f"<code>{line}</code>\n"
            if cmd == 'eval':
                return await act(text)
            await m.reply(text)
        except:
            traceback_string = traceback.format_exc()
            text = f"Exception while sending output:\n{traceback_string}"
            if cmd == 'eval':
                return await act(text)
            await m.reply(text)