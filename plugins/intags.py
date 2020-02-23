from pyrogram import Client, Filters
import re
import io
import html
import traceback
import subprocess
from contextlib import redirect_stdout
from config import cmds
from db import db

@Client.on_message(Filters.regex(r'.*<py>.+</py>', re.S) & Filters.me)
async def pytag(client, message):
    for match in re.finditer(r'<py>(.+?)</py>', message.text):
        strio = io.StringIO()
        code = match[1].strip()
        exec('async def __ex(client, message): ' + ' '.join('\n ' + l for l in code.split('\n')))
        with redirect_stdout(strio):
            try:
                await locals()["__ex"](client, message)
            except:
                return await message.reply_text(html.escape(traceback.format_exc()), parse_mode="HTML")
    
        if strio.getvalue():
            out = f"{html.escape(strio.getvalue())}"
        else:
            out = "<py></py>"
        message.text = message.text.replace(match[0], html.escape(out))
    await message.edit(message.text)

@Client.on_message(Filters.regex(r'.*<sh>.+</sh>') & Filters.me)
async def shtag(client, message):
    for match in re.finditer(r'<sh>(.+?)</sh>', message.text):
        out = subprocess.getstatusoutput(match[1])[1] or '<sh></sh>'
        message.text = message.text.replace(match[0], html.escape(out))
    await message.edit(message.text)

@Client.on_message(Filters.regex(r'.*<#.+?>') & Filters.me)
async def sharptag(client, message):
    changed = False
    for match in re.finditer(r'<#(.+?)>', message.text):
        note_key = match[1]
        exists = note_key in db['notes']
        
        if exists:
            changed = True
            note_obj = db['notes'][note_key]
            if note_obj['type'] == 'text':
                text = note_obj['value']
                message.text = message.text.replace(match[0], html.escape(text))
    if changed:
        await message.edit(message.text)
        

cmds.update({
    '<py>':'Run the python code inside the tag and replace it with the result',
    '<sh>':'Run the shell command inside the tag and replace it with the result',
    '<#%note>': "Search for a note named %note (replace with the name of the wanted note) and replace the tag with it",
})