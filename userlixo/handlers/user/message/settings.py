from userlixo.handlers.bot.settings import on_settings_u
from pyrogram import Client, filters

@Client.on_message(filters.su_cmd('settings'))
async def on_settings_txt(c, m):
    await on_settings_u(c,m)