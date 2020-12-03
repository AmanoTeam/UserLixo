from userlixo.handlers.bot.upgrade import on_upgrade_u
from pyrogram import Client, filters

@Client.on_message(filters.su_cmd('upgrade'))
async def on_upgrade_m(c, m):
    await on_upgrade_u(c, m)
