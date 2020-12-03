from pyrogram import Client, filters
from userlixo.config import plugins
from userlixo.utils import shell_exec
import re, os
import platform
import pyromod, pyrogram
@Client.on_message(filters.su_cmd('info'))
async def on_info(c, m):
    lang = m._lang
    act = m.edit if await filters.me(c,m) else m.reply
    
    pid = os.getpid()
    uptime = (await shell_exec("ps -eo pid,etime | grep "+str(pid)+" | awk '{print $2}'"))[0]
    
    uname = (await shell_exec('uname -mons'))[0]
    local_version = int((await shell_exec('git rev-list --count HEAD'))[0])
    remote_version = int((await shell_exec("""curl -s -I -k 'https://api.github.com/repos/AmanoTeam/UserLixo/commits?per_page=1' | grep -oE '&page=[0-9]+>; rel="last"' | grep -oE '[0-9]+' """))[0])
    python_version = platform.python_version()
    pyrogram_version = pyrogram.__version__
    pyromod_version = pyromod.__version__
    
    ul_status = lang.info_upgradable_to(version=remote_version) if local_version < remote_version else lang.info_lastest
    
    user_plugins = len([x for x in plugins['user']])
    bot_plugins = len([x for x in plugins['bot']])
    plugins_total = user_plugins+bot_plugins
    append_plugins = f"\n├ 👤 {user_plugins}\n└ 👾 {bot_plugins}" if plugins_total else ''
    
    text = lang.info_text(
        pid=pid,
        uptime=uptime,
        uname=uname,
        local_version=local_version,
        ul_status=ul_status,
        python_version=python_version,
        pyromod_version=pyromod_version,
        pyrogram_version=pyrogram_version,
        plugins_total=plugins_total,
        append_plugins=append_plugins
    )
    await act(text)
