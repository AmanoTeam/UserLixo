from userlixo.database import Config
from datetime import datetime
from pyrogram import Client, filters
from pyromod.helpers import ikb
from userlixo.utils import shell_exec, timezone_shortener
import os, re, sys

@Client.on_callback_query(filters.sudoers & filters.regex('^upgrade$'))
async def on_upgrade_cq(c, cq):
    await on_upgrade_u(c,cq)

async def on_upgrade_u(c, u):
    lang = u._lang
    is_query = hasattr(u, 'data')
    is_inline = is_query and not u.message
    from_where = '_bot' if is_query else ''
    act = u.edit if is_query else u.reply
    keyb = ikb([
        [(lang.back, 'start')]
    ])
    try:
        with open(".git/HEAD") as f:
            branch = f.read().split("/")[-1].rstrip()
    except FileNotFoundError:
        return await act(lang.upgrade_error_not_git, keyb)
    
    stdout, process = await shell_exec(f"git fetch && git status -uno")
    
    if process.returncode != 0:
        await act(lang.upgrade_failed(branch=branch, code=process.returncode, output=stdout), keyb)
        return await shell_exec("git merge --abort")
    
    if "Your branch is up to date" in stdout:
        title,p = await shell_exec('git log --format="%B" -1')
        rev,p = await shell_exec('git rev-parse --short HEAD')
        date,p = await shell_exec('git log -1 --format=%cd --date=format:"%d/%m %H:%M"')
        timezone,p = await shell_exec('git log -1 --format=%cd --date=format:"%z"')
        local_version = int((await shell_exec('git rev-list --count HEAD'))[0])
        
        timezone = timezone_shortener(timezone)
        date += f' ({timezone})'
        
        args = []
        if is_query:
            args.append(keyb)
        return await act(lang.upgrade_alert_already_uptodate(title=title, rev=rev, date=date, local_version=local_version), *args)

    msg = await act(lang.upgrading_now_alert)
    
    stdout, process = await shell_exec(f'git pull --no-edit origin {branch}')
    if process.returncode != 0:
        await msg.edit(lang.upgrade_failed(branch=branch, code=process.returncode, output=stdout), keyb)
        return await shell_exec("git merge --abort")
    
    await Config.filter(key="restarting_alert").delete()
    message_id = u.inline_message_id if is_inline else msg.message_id
    chat_id = 'inline' if is_inline else msg.chat.id
    await Config.create(**{"key": "restarting_alert", "value": f'{message_id}|{chat_id}|{datetime.now().timestamp()}|upgrade{from_where}'})
    args = [sys.executable, '-m', 'userlixo']
    if '--no-update' in sys.argv:
        args.append('--no-update')
    os.execv(sys.executable, args)