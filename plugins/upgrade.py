import os
import sys
import asyncio

from pyrogram import Client, filters

from config import cmds

from db import db, save

@Client.on_message(filters.command("upgrade", prefixes=".") & filters.me)
async def upgrade(client, message):
    try:
        with open(os.path.join(".git", "HEAD")) as f:
            branch = f.read().split("/")[-1].rstrip()
    except FileNotFoundError:
        return await message.edit_text("Error: You must be inside a git repository to upgrade.")

    parts = message.text.split(maxsplit=1)
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
