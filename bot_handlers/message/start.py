from pyrogram import Client, filters
from pyromod.helpers import ikb
from utils import shell_exec
import os, re, sys
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

@Client.on_callback_query(filters.sudoers & filters.regex('^upgrade$'))
async def onupgrade(c, cq):
    lang = cq.lang
    keyb = ikb([
        [(lang.back, 'start')]
    ])
    try:
        with open(".git/HEAD") as f:
            branch = f.read().split("/")[-1].rstrip()
    except FileNotFoundError:
        return await cq.edit(lang.upgrade_error_not_git, keyb)
    
    stdout, process = await shell_exec(f"git fetch && git status -uno")
    
    if process.returncode != 0:
        await cq.edit(lang.upgrade_failed(branch=branch, code=process.returncode, output=stdout), keyb)
        return await shell_exec("git merge --abort")
    
    if "Your branch is up to date" in stdout:
        title,p = await shell_exec('git log --format="%B" -1')
        rev,p = await shell_exec('git rev-parse --short HEAD')
        date,p = await shell_exec("git log -1 --format=%cd --date=local")
        return await cq.edit(lang.upgrade_alert_already_uptodate(title=title, rev=rev, date=date), keyb)
    
    if 'DYNO' not in os.environ:
        msg = await cq.edit(lang.checking_packages_updates)
        output, p = await shell_exec('pip list -o')
        with open('requirements-sqlite.txt') as f:
            requirements = f.read().splitlines()
        upgradable = []
        for req in requirements:
            if req in output:
                match = re.search(f'(?P<name>{req})\s+(?P<current>\S+)\s+(?P<last>\S+)', output)
                upgradable.append(f"<code>{match['name']} ({match['current']} -> {match['last']})")
        upgradable = '\n'.join(upgradable)
        
        keyboard = ikb([
            [(lang.upgrade_pip_continue, 'upgrade_pip start')],
            [(lang.upgrade_not_pip, 'upgrade_not_pip start')],
            [(lang.cancel, 'start')]
        ])
        
        if len(upgradable):
            text = lang.ask_upgrade_pip_pkgs
            text.escape_html = False
            return await cq.edit(text(upgradable=upgradable), keyboard)

    msg = await cq.edit(lang.upgrading_now_alert)
    
    stdout, process = await shell_exec(f'git pull --no-edit origin {branch}')
    if process.returncode != 0:
        await cq.edit(lang.upgrade_failed(branch=branch, code=process.returncode, output=stdout), keyb)
        return await shell_exec("git merge --abort")
    
    await Config.filter(key="restarting_alert").delete()
    await Config.create(**{"key": "restarting_alert", "value": f'{msg.message_id}|{msg.chat.id}|{datetime.now().timestamp()}|upgrade_start'})
    os.execl(sys.executable, sys.executable, *sys.argv)

@Client.on_callback_query(filters.sudoers & filters.regex('^upgrade_pip'))
async def onupgradepip(c, cq):
    lang = cq.lang
    await cq.edit(lang.upgrading_pip_packages)
    
    branch = (await shell_exec('git rev-parse --abbrev-ref HEAD'))[0]
    output, p = await shell_exec('pip install -Ur requirements-sqlite.txt')
    if p.returncode != 0:
        kwargs = {}
        keyb = ikb([
            [(lang.back, 'start')]
        ])
        
        if cq.data.endswith('start'):
            kwargs.update(reply_markup=keyb)
        
        await cq.edit(lang.upgrade_failed(branch=branch, code=p.returncode, output=output), **kwargs)
        return await shell_exec("git merge --abort")
    
    await cq.edit(lang.upgrading_now_alert)
    await Config.filter(key="restarting_alert").delete()
    
    extra = 'upgrade_start' if cq.data.endswith('start') else 'upgrade'
    await Config.create(**{"key": "restarting_alert", "value": f'{cq.inline_message_id}|inline|{datetime.now().timestamp()}|{extra}'})
    os.execl(sys.executable, sys.executable, *sys.argv)

@Client.on_callback_query(filters.sudoers & filters.regex('^upgrade_not_pip'))
async def onupgradenotpip(c, cq):
    lang = cq.lang
    await cq.edit(lang.upgrading_pip_packages)
    
    await cq.edit(lang.upgrading_now_alert)
    await Config.filter(key="restarting_alert").delete()
    
    extra = 'upgrade_start' if cq.data.endswith('start') else 'upgrade'
    await Config.create(**{"key": "restarting_alert", "value": f'{cq.inline_message_id}|inline|{datetime.now().timestamp()}|{extra}'})
    os.execl(sys.executable, sys.executable, *sys.argv)

@Client.on_callback_query(filters.sudoers & filters.regex('^upgrade_cancel'))
async def onupgradecancel(c, cq):
    lang = cq.lang
    await cq.edit(lang.upgrade_canceled)

@Client.on_callback_query(filters.sudoers & filters.regex('^restart'))
async def onrestartbtn(c, cq):
    lang = cq.lang
    m = cq.message
    msg = await cq.edit(lang.restarting_now_alert, None)
    await Config.filter(key="restarting_alert").delete()
    await Config.create(**{"key": "restarting_alert", "value": f'{msg.message_id}|{msg.chat.id}|{datetime.now().timestamp()}|restart_start'})
    os.execl(sys.executable, sys.executable, *sys.argv)