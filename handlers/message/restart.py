import os
import sys
from database import Config
from datetime import datetime
from pyrogram import Client, filters

@Client.on_message(filters.sudoers & filters.su_cmd('restart'))
async def onrestart(c, m):
    lang = m.lang
    act = m.edit if await filters.me(c,m) else m.reply
    
    msg = await act(lang.restarting_now_alert)
    await Config.filter(key="restarting_alert").delete()
    await Config.create(key="restarting_alert", value=f'{msg.message_id}|{msg.chat.id}|{datetime.now().timestamp()}|restart')
    
    os.execl(sys.executable, sys.executable, *sys.argv)