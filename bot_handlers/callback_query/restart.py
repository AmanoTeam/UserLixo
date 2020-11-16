from database import Config
from datetime import datetime
from pyrogram import Client, filters
import os, sys

@Client.on_callback_query(filters.sudoers & filters.regex('^restart'))
async def onrestartbtn(c, cq):
    lang = cq.lang
    msg = await cq.edit(lang.restarting_now_alert)
    await Config.filter(key="restarting_alert").delete()
    await Config.create(**{"key": "restarting_alert", "value": f'{msg.message_id}|{msg.chat.id}|{datetime.now().timestamp()}|restart_start'})
    os.execl(sys.executable, sys.executable, *sys.argv)
