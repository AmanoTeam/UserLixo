from config import sudoers
from pyrogram import Client, filters

@Client.on_message(filters.su_cmd('settings'))
async def on_settings(client, message):
    lang = message.lang
    keyboard = [
        [(lang.language, 'setting_language')],
        [(lang.sudoers, 'setting_sudoers')],
        [(lang.env_vars, 'setting_env')]
    ]
    await message.reply(lang.settings_text, keyboard)