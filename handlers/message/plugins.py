from bot_handlers.callback_query.plugins import onplugins
from bot_handlers.message.add_plugin import onaddplugin_txt
from pyrogram import Client, filters

@Client.on_message(filters.su_cmd('plugins$'))
async def onplugins_txt(c,m):
    print(1, m.matches, m.text)
    m.matches = [{"page": 0}]
    await onplugins(c,m)