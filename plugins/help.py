import html

from config import cmds
from pyrogram import Client, Filters

@Client.on_message(Filters.command("help", prefixes=".") & Filters.me)
async def chelp(client, message):
    if message.text[6:]:
        a = message.text[6:]
        if a in cmds:
            await message.edit(f'<code>{html.escape(a)}</code>: {cmds[a]}')
        else:
            await message.edit(f'Command \'<code>{html.escape(a)}</code>\' not found.')
            
    else:
        a = ['<code>{}</code>: {}'.format(html.escape(i), cmds[i]) for i in cmds]
        await message.edit('\n'.join(a))

cmds.update({'.help':'List all the commands'})