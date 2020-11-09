from database import Config
from datetime import datetime
from pyrogram import Client, filters
from utils import shell_exec
import asyncio
import os
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
    
    stdout, process = await shell_exec(f"git pull --no-edit origin {branch}")
    
    if process.returncode != 0:
        await act(lang.upgrade_failed(branch=branch, code=process.returncode, output=stdout))
        return await shell_exec("git merge --abort")
        
    if "Already up to date." in stdout:
        title,p = await shell_exec('git log --format="%B" -1')
        rev,p = await shell_exec('git rev-parse --short HEAD')
        date,p = await shell_exec("git log -1 --format=%cd --date=local")
        return await act(lang.upgrade_alert_already_uptodate(title=title, rev=rev, date=date))
    msg = await act(lang.restarting_now_alert)
    
    await Config.filter(key="restarting_alert").delete()
    await Config.create(key="restarting_alert", value=f'{msg.message_id}|{msg.chat.id}|{datetime.now().timestamp()}|upgrade')
    
    os.execl(sys.executable, sys.executable, *sys.argv)