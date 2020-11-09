from config import sudoers
from pyrogram import Client, filters
from pyromod.helpers import ikb

@Client.on_callback_query(filters.sudoers & filters.regex('^settings( start)?'))
async def on_settings(client, query):
    lang = query.lang
    keyboard = [
        [(lang.language, 'setting_language')],
        [(lang.sudoers, 'setting_sudoers')],
        [(lang.env_vars, 'setting_env')]
    ]
    if query.data.endswith('start'):
        keyboard.append([ (lang.back, 'start') ])
    keyboard = ikb(keyboard)
    await query.edit(lang.settings_text, keyboard)