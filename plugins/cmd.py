import asyncio

from pyrogram import Client, Filters

from config import cmds


@Client.on_message(Filters.command("cmd", prefixes=".") & Filters.me)
async def cmd(client, message):
    text = message.text[5:]
    proc = await asyncio.create_subprocess_shell(text,
                                                stdout=asyncio.subprocess.PIPE,
                                                stderr=asyncio.subprocess.STDOUT)
    ex = await proc.communicate()
    res = ex[0].decode().rstrip() or 'Comando executado'
    await message.edit(res)

cmds.update({'.cmd':'Execute a command in the CMD'})
