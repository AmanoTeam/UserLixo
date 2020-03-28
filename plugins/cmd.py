import asyncio
import re

from config import cmds
from pyrogram import Client, Filters

@Client.on_message(Filters.command("cmd", prefixes=".") & Filters.me)
async def cmd(client, message):
    code = message.text.split(' ', 1)[1]
    
    edit_mode = False
    if re.match('(-e|--edit) ', code):
    	code = re.sub('^(-e|--edit) ', '', code)
    	edit_mode = True
    
    reply_mode = False
    if re.match('(-r|--reply) ', code):
    	code = re.sub('^(-r|--reply) ', '', code)
    	reply_mode = True
    
    process = await asyncio.create_subprocess_shell(
		code,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT
    )
    result = (await process.communicate())[0].decode().rstrip()
    
    if edit_mode and result:
    	await message.edit(result)
    elif reply_mode:
    	text = lang.COMMAND_RESULT(

cmds.update({'.cmd':'Execute a command in the CMD'})
