from config import sudoers
from pyrogram import Client, filters

@Client.on_message(filters.su_cmd('settings'))
async def on_settings(c, m):
    lang = m.lang
    keyboard = [
        [(lang.language, 'setting_language')],
        [(lang.sudoers, 'setting_sudoers')],
        [(lang.env_vars, 'setting_env')]
    ]
    await m.reply(lang.settings_text, keyboard)