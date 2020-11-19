from config import load_env, sudoers, langs, client, bot
from database import connect_database, Config
from datetime import datetime
from pyrogram import idle
from pyromod.helpers import ikb
from rich import print, box
from rich.panel import Panel
from tortoise import run_async
from utils import info, shell_exec
import asyncio
import os
import rich

async def alert_startup():
    plugins = [(handler.user_callback if hasattr(handler, 'user_callback') else handler.callback) for group in client.dispatcher.groups.values() for handler in group]
    
    plugins_count = len(plugins)
    
    started_alert = f"""🚀 UserLixo launched. <code>{plugins_count}</code> plugins loaded.
- <b>app_version</b>: <code>{client.app_version}</code>
- <b>device_model</b>: <code>{client.device_model}</code>
- <b>system_version</b>: <code>{client.system_version}</code>
"""
    try:
        await bot.send_message(info['user']['username'], started_alert)
    except:
        await client.send_message(os.getenv('LOGS_CHAT'), started_alert)

async def main():
    await connect_database()
    await load_env()
    
    await client.start()
    info['user'] = await client.get_me()
    sudoers.append(info['user'].id)
    
    await bot.start()
    info['bot'] = await bot.get_me()
    
    # Editing restaring alert
    restarting_alert = await Config.filter(key="restarting_alert")
    if len(restarting_alert) > 1:
        restarting_alert = []
        await Config.filter(key="restarting_alert").delete()
    
    if restarting_alert:
        restarting_alert = restarting_alert[0]
        
        parts = restarting_alert.value.split('|')
        if len(parts) == 3:
            parts.append('restart')
        message_id, chat_id, cmd_timestamp, from_cmd = parts
        
        cmd_timestamp = float(cmd_timestamp)
        now_timestamp = datetime.now().timestamp()
        diff = round(now_timestamp-cmd_timestamp, 2)
        
        title,p = await shell_exec('git log --format="%B" -1')
        rev,p = await shell_exec('git rev-parse --short HEAD')
        date,p = await shell_exec("git log -1 --format=%cd --date=local")
        local_version = int((await shell_exec('git rev-list --count HEAD'))[0])
        
        kwargs = {}
        text = langs.restarted_alert
        if from_cmd.startswith('upgrade'):
            text = langs.upgraded_alert
        text = text(title=title, rev=rev, date=date, seconds=diff, local_version=local_version)
        
        if from_cmd.endswith('_start'):
            keyb = ikb([
                [(langs.back, 'start')]    
            ])
            kwargs.update(reply_markup=keyb)
        
        try:
            editor = client
            if from_cmd.endswith('_start'):
                editor = bot
            if chat_id == 'inline':
                await bot.edit_inline_text(message_id, text, **kwargs)
            else:
                await editor.edit_message_text(int(chat_id), int(message_id), text, **kwargs)
        except Exception as e:
            print(f'[yellow]Failed to edit the restarting alert. Maybe the message has been deleted or somehow it became inacessible.\n>> {e}[/yellow]')
        await Config.get(id=restarting_alert.id).delete()
    
    # Showing alert in cli
    commit_date,p = await shell_exec("git log -1 --format=%cd --date=local")
    account = '@'+info['user']['username'] if info['user']['username'] else info['user']['id']
    text = f":ok: [bold green]UserLixo is running[/bold green] :ok:"
    
    userlixo_info = dict(
        Account=account,
        Bot=info['bot']['username'],
        Prefixes=os.getenv('PREFIXES'),
        Logs_chat=os.getenv('LOGS_CHAT'),
        Sudoers=', '.join([*set(map(str, sudoers))]), # using set() to make the values unique
        Commit_date=commit_date
    )
    for k,v in userlixo_info.items():
        text += f"\n[dim cyan]{k}:[/dim cyan] [dim]{v}[/dim]"

    print(Panel.fit(text, border_style='green', box=box.ASCII))
    
    # Sending alert via Telegram
    await alert_startup()
    
    await idle()
    
run_async(main())