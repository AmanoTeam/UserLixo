from config import sudoers
from pyrogram import Client, Filters

@Client.on_message(Filters.regex(r'^\Wsettings') & Filters.sudoers)
async def on_settings(client, message):
    lang = message.lang
    keyboard = [
        [(lang.language, 'setting_language')],
        [(lang.sudoers, 'setting_sudoers')],
        [(lang.env_vars, 'setting_env')]
    ]
    await message.reply(lang.settings_text, keyboard)