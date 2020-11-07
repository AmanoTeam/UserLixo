from config import load_env, sudoers, client, bot
from database import connect_database
from pyrogram import idle
from tortoise import run_async
from utils import info
import os

async def alert_startup():
    plugins = [(handler.user_callback if hasattr(handler, 'user_callback') else handler.callback) for group in client.dispatcher.groups.values() for handler in group]
    
    plugins_count = len(plugins)
    
    started_alert = f"""🚀 UserLixo launched. <code>{plugins_count}</code> plugins loaded.
- <b>app_version</b>: <code>{client.app_version}</code>
- <b>device_model</b>: <code>{client.device_model}</code>
- <b>system_version</b>: <code>{client.system_version}</code>
"""
    await client.send_message(os.getenv('LOGS_CHAT'), started_alert)

async def main():
    await connect_database()
    await load_env()
    
    await client.start()
    info['user'] = await client.get_me()
    sudoers.append(info['user'].id)
    
    await bot.start()
    info['bot'] = await bot.get_me()
    
    await alert_startup()
    await idle()
    
run_async(main())