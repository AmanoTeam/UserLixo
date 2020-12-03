from userlixo.handlers.bot.help import on_help_u
from pyrogram import Client, filters

@Client.on_message(filters.su_cmd('help'))
async def on_help_m(c, m):
    await on_help_u(c,m)