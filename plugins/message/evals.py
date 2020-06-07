import asyncio
import html
import os
import re
import traceback

from config import sudoers
from pyrogram import Client, Filters
from meval import meval

@Client.on_message(Filters.su_cmd(r"^\Weval\s+(?P<code>.+)", re.S))
async def evals(client, message):
    eval_code = message.matches[0]['code']
    
    # Shortcuts that will be available for the user code
    reply = message.reply_to_message
    user = (reply or message).from_user
    
    try:
        output = await meval(eval_code, globals(), **locals())
    except:
        traceback_string = traceback.format_exc()
        return await message.reply(f"Exception while running the code:\n{traceback_string}")
    else:
        try:
            output = html.escape(str(output)) # escape html special chars
            text = ''
            for line in output.splitlines():
                text += f"<code>{line}</code>\n"
            await message.reply(text)
        except:
            traceback_string = traceback.format_exc()
            return await message.reply(f"Exception while sending output:\n{traceback_string}")