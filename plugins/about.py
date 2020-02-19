from config import cmds

from pyrogram import Client, Filters

@Client.on_message(Filters.command("help", prefixes=".") & Filters.me)
async def chelp(client, message):
    if message.text[6:]:
        a = message.text[6:]
        if a:
            await message.edit(cmds[a])
    else:
        a = ['{}: {}'.format(i, cmds[i]) for i in cmds]
        await message.edit('\n'.join(a))