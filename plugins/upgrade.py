import os
import subprocess
import sys
import threading
import time

from pyrogram import Client, Filters

from config import git_repo
from db import db, save


@Client.on_message(Filters.command("upgrade", prefixes=".") & Filters.me)
async def uprade(client, message):
    a = await client.send_message('me', 'Atualizando...')
    out = subprocess.getstatusoutput('git pull {}'.format(' '.join(git_repo)))[1]
    a.edit(f'Resultado da atualização:\n{out}')
    sent = await message.edit('Reiniciando...')
    db["restart"] = {'cid': message.chat.id, 'mid': sent.message_id}
    save(db)
    time.sleep(1)
    os.execl(sys.executable, sys.executable, *sys.argv)
    del threading.Thread
