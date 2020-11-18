from ..message.add_plugin import onaddplugin_txt
from pyrogram import Client, filters

@Client.on_callback_query(filters.sudoers & filters.regex('^add_plugin'))
async def onaddplugin_cb(c, cq):
    await onaddplugin_txt(c,cq)