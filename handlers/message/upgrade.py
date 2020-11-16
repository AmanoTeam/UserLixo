from database import Config
from datetime import datetime
from pyrogram import Client, filters
from utils import shell_exec
import asyncio
import os
import re
import sys

@Client.on_message(filters.su_cmd('upgrade'))
async def onupgrade(c, m):
    lang = m.lang
    act = m.edit if await filters.me(c,m) else m.reply
    try:
        with open(".git/HEAD") as f:
            branch = f.read().split("/")[-1].rstrip()
    except FileNotFoundError:
        return await act(lang.upgrade_error_not_git)
    
    stdout, process = await shell_exec("git fetch && git status -uno")
    
    if process.returncode != 0:
        await act(lang.upgrade_failed(branch=branch, code=process.returncode, output=stdout))
        return await shell_exec("git merge --abort")
        
    if "Your branch is up to date" in stdout:
        title,p = await shell_exec('git log --format="%B" -1')
        rev,p = await shell_exec('git rev-parse --short HEAD')
        date,p = await shell_exec("git log -1 --format=%cd --date=local")
        return await act(lang.upgrade_alert_already_uptodate(title=title, rev=rev, date=date))
    
    if 'DYNO' not in os.environ:
        msg = await act(lang.checking_packages_updates)
        output, p = await shell_exec('pip list -o')
        with open('requirements-sqlite.txt') as f:
            requirements = f.read().splitlines()
        upgradable = []
        for req in requirements:
            if req in output:
                match = re.search(f'(?P<name>{req})\s+(?P<current>\S+)\s+(?P<last>\S+)', output)
                upgradable.append(f"<code>{match['name']} ({match['current']} -> {match['last']})")
        upgradable = '\n'.join(upgradable)
        
        keyboard = [
            [(lang.upgrade_pip_continue, 'upgrade_pip')],
            [(lang.upgrade_not_pip, 'upgrade_not_pip')],
            [(lang.cancel, 'upgrade_cancel')]
        ]
        if len(upgradable):
            text = lang.ask_upgrade_pip_pkgs
            text.escape_html = False
            await m.reply(text(upgradable=upgradable), keyboard)
            
            if await filters.me(c,m):
                await m.delete()
            else:
                await msg.delete()
            return
    
    msg = await act(lang.upgrading_now_alert)
    
    stdout, process = await shell_exec(f'git pull --no-edit origin {branch}')
    if process.returncode != 0:
        await msg.edit(lang.upgrade_failed(branch=branch, code=process.returncode, output=stdout))
        return await shell_exec("git merge --abort")
    
    await Config.filter(key="restarting_alert").delete()
    await Config.create(key="restarting_alert", value=f'{msg.message_id}|{msg.chat.id}|{datetime.now().timestamp()}|upgrade')
    
    os.execl(sys.executable, sys.executable, *sys.argv)