import os
import sys
import asyncio

from pyrogram import Client, Filters

from config import cmds

from db import db, save


@Client.on_message(Filters.command("upgrade", prefixes=".") & Filters.me)
async def upgrade(client, message):
    await message.edit("Upgrading sources...")
    proc = await asyncio.create_subprocess_shell(f"git pull --no-edit",
                                                 stdout=asyncio.subprocess.PIPE,
                                                 stderr=asyncio.subprocess.STDOUT)
    stdout = (await proc.communicate())[0]
    if proc.returncode == 0:
        if "Already up to date." in stdout.decode():
            await message.edit("There's nothing to upgrade.")
        else:
            await message.edit(("reiniciando..."))
            db["restart"] = {'cid': message.chat.id, 'mid': message.message_id}
            save(db)
            os.execl(sys.executable, sys.executable, *sys.argv)
    else:
        await message.edit(f"Upgrade failed (process exited with {proc.returncode}):\n{stdout.decode()}")
        proc = await asyncio.create_subprocess_shell("git pull --no-edit")
        stdout = await proc.communicate()

cmds.update({'.upgrade':'Upgrade a bot souce'})
