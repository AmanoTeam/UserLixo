from ..callback_query.plugins import onplugins
from pyrogram import Client, filters

@Client.on_message(filters.sudoers & filters.regex('^/plugins( (?P<page>\d+))?'))
async def onplugins_txt(c,m):
    m.from_bot_handler = True
    await onplugins(c,m)