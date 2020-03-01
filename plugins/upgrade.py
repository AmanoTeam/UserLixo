import os
import sys
import asyncio

from pyrogram import Client, Filters

from config import cmds

from db import db, save

@Client.on_message(Filters.command("upgrade", prefixes=".") & Filters.me)
async def upgrade(client, message):
    branch = 'master'
    parts = message.text.split(' ', 1)
    if len(parts) == 2:
        branch = parts[1]
    await message.edit(f"Upgrading source from branch '{branch}'...")
    proc = await asyncio.create_subprocess_shell(f"git pull --no-edit origin {branch}",
                                                 stdout=asyncio.subprocess.PIPE,
                                                 stderr=asyncio.subprocess.STDOUT)
    stdout = (await proc.communicate())[0]
    if proc.returncode == 0:
        if "Already up to date." in stdout.decode():
            await message.edit(f"There's nothing to upgrade from branch '{branch}'.")
        else:
            await message.edit(("Restarting..."))
            db["restart"] = {'cid': message.chat.id, 'mid': message.message_id, 'branch': branch}
            save(db)
            os.execl(sys.executable, sys.executable, *sys.argv)
    else:
        await message.edit(f"Upgrade from branch '{branch}' failed (process exited with {proc.returncode}):\n{stdout.decode()}")
        proc = await asyncio.create_subprocess_shell("git merge --abort")
        await proc.communicate()
        
cmds.update({'.upgrade':'Upgrade the userbot source'})
