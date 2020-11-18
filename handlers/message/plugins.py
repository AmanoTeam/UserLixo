from bot_handlers.callback_query.plugins import onplugins
from pyrogram import Client, filters

@Client.on_message(filters.su_cmd('plugins'))
async def onplugins_txt(c,m):
    m.matches = [{"page": 0}]
    await onplugins(c,m)