import os
from config import sudoers
from database import Config
from pyrogram import Client, Filters
from pyromod.helpers import ikb, array_chunk

def cmd(pattern, *args, **kwargs):
    return Filters.regex(pattern, *args, **kwargs) & Filters.user(sudoers)

@Client.on_callback_query(cmd('^setting_language'))
async def on_setting_language(client, query):
    lang = query.lang
    buttons = []
    for code,obj in lang.strings.items():
        text, data = (f"✅ {obj['NAME']}", 'noop') if obj['language_code'] == lang.code else (obj['NAME'], f"set_language {obj['language_code']}")
        buttons.append((text, data))
    lines = array_chunk(buttons, 2)
    lines.append([(lang.back, 'settings')])
    keyboard = ikb(lines)
    await query.edit(lang.choose_language, keyboard)

@Client.on_callback_query(cmd(r'^set_language (?P<code>\w+)'))
async def on_set_language(client, query):
    lang = query.lang
    match = query.matches[0]
    lang = lang.get_language(match['code'])
    await Config.get(key='LANGUAGE').update(value=lang.code)
    os.environ['LANGUAGE'] = lang.code
    buttons = []
    for code,obj in lang.strings.items():
        text, data = (f"✅ {obj['NAME']}", 'noop') if obj['language_code'] == lang.code else (obj['NAME'], f"set_language {obj['language_code']}")
        buttons.append((text, data))
    lines = array_chunk(buttons, 2)
    lines.append([(lang.back, 'settings')])
    keyboard = ikb(lines)
    await query.edit(lang.choose_language, keyboard, {"text": lang.language_chosen})
