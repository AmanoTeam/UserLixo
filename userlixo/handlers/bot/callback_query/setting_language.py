import os
from userlixo.config import sudoers
from userlixo.database import Config
from pyrogram import Client, filters
from pyromod.helpers import ikb, array_chunk

@Client.on_callback_query(filters.sudoers & filters.regex('^setting_language'))
async def on_setting_language(c, cq):
    lang = cq._lang
    buttons = []
    for code,obj in lang.strings.items():
        text, data = (f"✅ {obj['NAME']}", 'noop') if obj['LANGUAGE_CODE'] == lang.code else (obj['NAME'], f"set_language {obj['LANGUAGE_CODE']}")
        buttons.append((text, data))
    lines = array_chunk(buttons, 2)
    lines.append([(lang.back, 'settings')])
    keyboard = ikb(lines)
    await cq.edit(lang.choose_language, keyboard)

@Client.on_callback_query(filters.sudoers & filters.regex(r'^set_language (?P<code>\w+)'))
async def on_set_language(c, cq):
    lang = cq._lang
    match = cq.matches[0]
    lang = lang.get_language(match['code'])
    await Config.get(key='LANGUAGE').update(value=lang.code)
    os.environ['LANGUAGE'] = lang.code
    buttons = []
    for code,obj in lang.strings.items():
        text, data = (f"✅ {obj['NAME']}", 'noop') if obj['LANGUAGE_CODE'] == lang.code else (obj['NAME'], f"set_language {obj['LANGUAGE_CODE']}")
        buttons.append((text, data))
    lines = array_chunk(buttons, 2)
    lines.append([(lang.back, 'settings')])
    keyboard = ikb(lines)
    await cq.edit(lang.choose_language, keyboard, {"text": lang.language_chosen})
