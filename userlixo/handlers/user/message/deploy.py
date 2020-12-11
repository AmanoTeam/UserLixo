from datetime import datetime
from pyrogram import Client, filters
from userlixo.config import heroku_client, heroku_app
from userlixo.database import Config
from userlixo.utils import heroku_self_deploy
import os

@Client.on_message(filters.su_cmd('deploy'))
async def on_deploy(c, m):
    lang = m._lang
    act = m.edit if await filters.me(c,m) else m.reply
    if 'DYNO' not in os.environ:
        return await act(lang.not_running_in_heroku)
    
    msg = await act(lang.deploying_on_heroku)
    await Config.filter(key="restarting_alert").delete()
    message_id = msg.message_id
    chat_id = msg.chat.username if msg.chat.username else msg.chat.id
    await Config.create(**{"key": "restarting_alert", "value": f'{message_id}|{chat_id}|{datetime.now().timestamp()}|restart'})
    
    heroku_self_deploy(heroku_client, heroku_app)