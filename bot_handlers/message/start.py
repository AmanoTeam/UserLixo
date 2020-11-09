from pyrogram import Client, filters
from pyromod.helpers import ikb
from utils import shell_exec
import os, sys
from database import Config
from datetime import datetime

@Client.on_message(filters.sudoers & filters.regex('^/start'))
async def onstart(c, m):
    lang = m.lang
    keyb = ikb([
        [(lang.upgrade, 'upgrade'), [lang.restart, 'restart']],
        [(lang.plugins, 'plugins start')],
        [(lang.help, 'help start'), (lang.settings, 'settings start')]
    ])
    text = lang.start_text
    await m.reply(text, keyb)

@Client.on_callback_query(filters.sudoers & filters.regex('^start'))
async def onstartcb(c, cq):
    lang = cq.lang
    m = cq.message
    keyb = ikb([
        [(lang.upgrade, 'upgrade'), [lang.restart, 'restart']],
        [(lang.plugins, 'plugins start')],
        [(lang.help, 'help start'), (lang.settings, 'settings start')]
    ])
    text = lang.start_text
    await cq.edit(text, keyb)

@Client.on_callback_query(filters.sudoers & filters.regex('^upgrade'))
async def onupgrade(c, cq):
    lang = cq.lang
    m = cq.message
    keyb = ikb([
        [(lang.back, 'start')]
    ])
    try:
        with open(".git/HEAD") as f:
            branch = f.read().split("/")[-1].rstrip()
    except FileNotFoundError:
        return await cq.edit(lang.upgrade_error_not_git, keyb)
    
    stdout, process = await shell_exec(f"git pull --no-edit origin {branch}")
    
    if process.returncode == 0:
        if "Already up to date." in stdout:
            title,p = await shell_exec('git log --format="%B" -1')
            rev,p = await shell_exec('git rev-parse --short HEAD')
            date,p = await shell_exec("git log -1 --format=%cd --date=local")
            await cq.edit(lang.upgrade_alert_already_uptodate(title=title, rev=rev, date=date), keyb)
        else:
            msg = await m.edit(lang.restarting_now_alert)
            await Config.filter(key="restarting_alert").delete()
            await Config.create(**{"key": "restarting_alert", "value": f'{msg.message_id}|{msg.chat.id}|{datetime.now().timestamp()}|upgrade_start'})
            os.execl(sys.executable, sys.executable, *sys.argv)
    else:
        await cq.edit(lang.upgrade_failed(branch=branch, code=process.returncode, output=stdout), keyb)
        await shell_exec("git merge --abort")

@Client.on_callback_query(filters.sudoers & filters.regex('^restart'))
async def onrestartbtn(c, cq):
    lang = cq.lang
    m = cq.message
    msg = await cq.edit(lang.restarting_now_alert, None)
    await Config.filter(key="restarting_alert").delete()
    await Config.create(**{"key": "restarting_alert", "value": f'{msg.message_id}|{msg.chat.id}|{datetime.now().timestamp()}|restart_start'})
    os.execl(sys.executable, sys.executable, *sys.argv)