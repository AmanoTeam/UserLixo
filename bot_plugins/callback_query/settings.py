from config import sudoers
from pyrogram import Client, Filters
from pyromod.helpers import ikb

@Client.on_callback_query(Filters.su_regex('^settings$'))
async def on_settings(client, query):
    lang = query.lang
    keyboard = ikb([
        [(lang.language, 'setting_language')],
        [(lang.sudoers, 'setting_sudoers')],
        [(lang.env_vars, 'setting_env')]
    ])
    await query.edit(lang.settings_text, keyboard)