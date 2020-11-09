from database import Config
from datetime import datetime
from pyrogram import Client, filters
import asyncio
import os
import sys

@Client.on_message(filters.su_cmd('upgrade'))
async def onupgrade(c, m):
    lang = m.lang
    try:
        with open(".git/HEAD") as f:
            branch = f.read().split("/")[-1].rstrip()
    except FileNotFoundError:
        return await m.edit(lang.upgrade_error_not_git)

    await m.edit(lang.upgrade_starting_alert)
    
    process = await asyncio.create_subprocess_shell(f"git pull --no-edit origin {branch}",
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.STDOUT)
    
    stdout = (await process.communicate())[0]
    
    if process.returncode == 0:
        if "Already up to date." in stdout.decode():
            await m.edit(lang.upgrade_alert_already_uptodate)
        else:
            msg = await m.edit(lang.restarting_now_alert)
            await Config.create(**{"key": "restarting_alert", "value": f'{msg.message_id}|{msg.chat.id}|{datetime.now().timestamp()}'})
            os.execl(sys.executable, sys.executable, *sys.argv)
    else:
        await m.edit(lang.upgrade_failed(branch=branch, code=process.returncode, output=stdout.decode()))
        process = await asyncio.create_subprocess_shell("git merge --abort")
        await process.communicate()