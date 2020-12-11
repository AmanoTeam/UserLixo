import os, sys
os.system('clear')
# Update requirements
DGRAY = 'echo -e "\033[1;30m"'
YELLOW = 'echo -e "\033[0;33m"'
RESET = 'echo -e "\033[0m"'
unused_requirements = []
if 'DYNO' not in os.environ:
    if '--no-update' not in sys.argv:
        print('\033[0;32m[1/2] Updating requirements...\033[0m')
        os.system(f'{DGRAY}; {sys.executable} -m pip install -Ur requirements.txt; {RESET}')
        os.system('clear')
        # Update plugins requirements
        from userlixo.config import plugins
        from userlixo.utils import reload_plugins_requirements
        requirements, unused_requirements = reload_plugins_requirements(plugins)
        if os.path.exists('plugins-requirements.txt'):
            print('\033[0;32m[2/2] Updating plugins requirements...\033[0m')
            os.system(f'{DGRAY}; {sys.executable} -m pip install -Ur plugins-requirements.txt; {RESET}')
print('\033[0m')
os.system('clear')

from userlixo.config import load_env, sudoers, langs, user, bot, unload_inactive_plugins, plugins
from userlixo.database import connect_database, Config
from datetime import datetime
from pyrogram import idle
from pyromod.helpers import ikb
from rich import print, box
from rich.panel import Panel
from tortoise import run_async
from userlixo.utils import shell_exec, timezone_shortener, get_inactive_plugins, tryint
import aiocron
import glob
import platform
import pyromod, pyrogram
import re

async def alert_startup():
    local_version = int((await shell_exec('git rev-list --count HEAD'))[0])
    python_version = platform.python_version()
    pyrogram_version = pyrogram.__version__
    pyromod_version = pyromod.__version__
    system_uname = (await shell_exec('uname -mons'))[0]
    
    pid = os.getpid()
    uptime = (await shell_exec("ps -o pid,etime --no-headers -p "+str(pid)+" | awk '{print $2}' "))[0]
    
    user_plugins = len([x for x in plugins['user']])
    bot_plugins = len([x for x in plugins['bot']])
    plugins_total = user_plugins+bot_plugins
    append_plugins = f"\n├ 👤 {user_plugins}\n└ 👾 {bot_plugins}" if plugins_total else ''
    
    text = langs.started_alert(
        version=local_version,
        pid=pid,
        python_version=python_version,
        pyrogram_version=pyrogram_version,
        pyromod_version=pyromod_version,
        server_uname=system_uname,
        uptime=uptime,
        plugins_total=plugins_total,
        append_plugins=append_plugins,
    )
    if 'DYNO' not in os.environ and 'VIRTUAL_ENV' not in os.environ:
        text += '\n\n'+langs.not_virtualenv_alert
    logs_chat = os.getenv('LOGS_CHAT')
    if logs_chat and logs_chat != 'me':
        return await user.send_message(logs_chat, text)
    
    try:
        await bot.send_message(user.me.username, text)
    except:
        await user.send_message(logs_chat, text)

async def main():
    await connect_database()
    await load_env()
    os.system('clear')
    
    @aiocron.crontab('*/1 * * * *')
    async def clean_cache():
        for file in glob.glob('cache/*'):
            if not os.path.isfile(file):
                continue
            creation_time = datetime.fromtimestamp(
                os.path.getctime(file)
            )
            now_time = datetime.now()
            diff = now_time-creation_time
            minutes_passed = diff.total_seconds()/60
            
            if minutes_passed >= 10:
                os.remove(file)
    
    
    if 'DYNO' not in os.environ and not os.path.exists('user.session'):
        from userlixo.login import main as login
        await login()
        os.system('clear')
        
    
    await user.start()
    await bot.start()
    await unload_inactive_plugins()
    
    user.me = await user.get_me()
    bot.me = await bot.get_me()
    user.assistant = bot
    
    if user.me.id not in sudoers:
        sudoers.append(user.me.id)
    
    # Editing restaring alert
    restarting_alert = await Config.filter(key="restarting_alert")
    if len(restarting_alert) > 1:
        await Config.filter(key="restarting_alert").delete()
        restarting_alert = []
    
    if restarting_alert:
        restarting_alert = restarting_alert[0]
        
        parts = restarting_alert.value.split('|')
        message_id, chat_id, cmd_timestamp, from_cmd = parts
        
        cmd_timestamp = float(cmd_timestamp)
        now_timestamp = datetime.now().timestamp()
        diff = round(now_timestamp-cmd_timestamp, 2)
        
        title,p = await shell_exec('git log --format="%B" -1')
        rev,p = await shell_exec('git rev-parse --short HEAD')
        date,p = await shell_exec('git log -1 --format=%cd --date=format:"%d/%m %H:%M"')
        timezone,p = await shell_exec('git log -1 --format=%cd --date=format:"%z"')
        local_version = int((await shell_exec('git rev-list --count HEAD'))[0])
        
        timezone = timezone_shortener(timezone)
        date += f' ({timezone})'
        
        kwargs = {}
        text = langs.upgraded_alert if from_cmd.startswith('upgrade') else langs.restarted_alert
        
        text = text(
            rev=rev,
            date=date,
            seconds=diff,
            local_version=local_version
        )
        if 'DYNO' in os.environ and from_cmd.startswith('upgrade'):
            text += '\n\n'+langs.alert_need_deploy
        
        try:
            editor = bot if from_cmd.endswith('_bot') else user
            if editor == bot:
                keyb = ikb([
                    [(langs.back, 'start')]    
                ])
                kwargs.update(reply_markup=keyb)
            if chat_id == 'inline':
                await bot.edit_inline_text(message_id, text, **kwargs)
            else:
                await editor.edit_message_text(tryint(chat_id), tryint(message_id), text, **kwargs)
        except Exception as e:
            print(f'[yellow]Failed to edit the restarting alert. Maybe the message has been deleted or somehow it became inacessible.\n>> {e}[/yellow]')
        await Config.get(id=restarting_alert.id).delete()
    
    # Showing alert in cli
    date,p = await shell_exec('git log -1 --format=%cd --date=format:"%d/%m %H:%M"')
    timezone,p = await shell_exec('git log -1 --format=%cd --date=format:"%z"')
    local_version = int((await shell_exec('git rev-list --count HEAD'))[0])
    
    timezone = timezone_shortener(timezone)
    date += f' ({timezone})'
    mention = '@'+user.me.username if user.me.username else user.me.id
    text = f":ok: [bold green]UserLixo is running[/bold green] :ok:"
    
    userlixo_info = {
        "Version": local_version,
        "Account": mention,
        "Bot": '@'+bot.me.username,
        "Prefixes": os.getenv('PREFIXES'),
        "Logs_chat": os.getenv('LOGS_CHAT'),
        "Sudoers": ', '.join([*set(map(str, sudoers))]), # using set() to make the values unique
        "Commit_date": date
    }
    for k,v in userlixo_info.items():
        text += f"\n[dim cyan]{k}:[/dim cyan] [dim]{v}[/dim]"

    print(Panel.fit(text, border_style='green', box=box.ASCII))
    
    # Sending alert via Telegram
    try:
        await alert_startup()
    except Exception as e:
        print(f'[bold yellow]Error while sending startup alert to LOGS_CHAT: {e}')
    
    # Alert about unused requirements
    if unused_requirements:
        unused = ', '.join(unused_requirements)
        print(f'[yellow]The following packages are not required by plugins anymore: [/][cyan]{unused}')
        try:
            await user.send_message(os.getenv('LOGS_CHAT'), f"The following packages are not required by plugins anymore: {unused}")
        except Exception as e:
            print('Error while sending alert about unused_requirements:\n  > ', e)
    await idle()

if __name__ == '__main__':
    run_async(main())