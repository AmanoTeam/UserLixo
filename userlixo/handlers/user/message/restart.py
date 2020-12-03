from userlixo.handlers.bot.restart import on_restart_u
from pyrogram import Client, filters

@Client.on_message(filters.sudoers & filters.su_cmd('restart'))
async def on_restart(c, m):
    await on_restart_u(c,m)