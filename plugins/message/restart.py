import os
import sys
from database import Config
from datetime import datetime
from pyrogram import Client, filters

@Client.on_message(filters.sudoers & filters.su_cmd('restart'))
async def onrestart(c, m):
    lang = m.lang
    msg = await m.edit(lang.restarting_now_alert)
    await Config.create(**{"key": "restarting_alert", "value": f'{msg.message_id}|{msg.chat.id}|{datetime.now().timestamp()}'})
    os.execl(sys.executable, sys.executable, *sys.argv)