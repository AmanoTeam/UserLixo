from userlixo.handlers.bot.start import on_start_u
from pyrogram import Client, filters

@Client.on_message(filters.su_cmd('start'))
async def on_start_txt(c, m):
    await on_start_u(c,m)