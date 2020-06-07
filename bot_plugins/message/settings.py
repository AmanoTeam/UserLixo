from config import sudoers
from pyrogram import Client, Filters
from pyromod.helpers import ikb

@Client.on_message(Filters.su_cmd('^/settings'))
async def on_settings(client, message):
    lang = message.lang
    keyboard = ikb([
        [(lang.language, 'setting_language')],
        [(lang.sudoers, 'setting_sudoers')],
        [(lang.env_vars, 'setting_env')]
    ])
    await message.reply_text(lang.settings_text, reply_markup=keyboard)