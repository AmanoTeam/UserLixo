from pyrogram import Client, filters
from utils import shell_exec
import re, os

@Client.on_message(filters.su_cmd('info'))
async def on_info(c, m):
    lang = m.lang
    act = m.edit if await filters.me(c,m) else m.reply
    
    pid = os.getpid()
    uptime = (await shell_exec("ps -eo pid,etime | grep "+str(pid)+" | awk '{print $2}'"))[0]
    
    uname = (await shell_exec('uname -mons'))[0]
    local_version = int((await shell_exec('git rev-list --count HEAD'))[0])
    remote_version = int((await shell_exec("""curl -s -I -k 'https://api.github.com/repos/AmanoTeam/UserLixo/commits?per_page=1' | grep -oE '&page=[0-9]+>; rel="last"' | grep -oE '[0-9]+' """))[0])
    
    ul_status = lang.info_upgradable_to(version=remote_version) if local_version < remote_version else lang.info_lastest
    
    text = lang.info_text(
        pid=pid,
        uptime=uptime,
        uname=uname,
        local_version=local_version,
        remote_version=remote_version,
        ul_status=ul_status
    )
    await act(text)
