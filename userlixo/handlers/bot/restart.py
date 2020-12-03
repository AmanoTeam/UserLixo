from userlixo.database import Config
from datetime import datetime
from pyrogram import Client, filters
import os, sys

@Client.on_callback_query(filters.sudoers & filters.regex('^restart'))
async def on_restart_txt(c, m):
    await on_restart_u(c,m)

async def on_restart_u(c, u):
    lang = u._lang
    is_query = hasattr(u, 'data')
    is_inline = is_query and not u.message
    from_where = '_bot' if is_query else ''
    act = u.edit if await filters.me(c,u) or is_query else u.reply
    
    msg = await act(lang.restarting_now_alert)
    await Config.filter(key="restarting_alert").delete()
    
    message_id = u.inline_message_id if is_inline else msg.message_id
    chat_id = 'inline' if is_inline else msg.chat.id
    await Config.create(**{"key": "restarting_alert", "value": f'{message_id}|{chat_id}|{datetime.now().timestamp()}|restart{from_where}'})
    args = [sys.executable, '-m', 'userlixo']
    if '--no-update' in sys.argv:
        args.append('--no-update')
    os.execv(sys.executable, args)
