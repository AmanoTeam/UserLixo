from pyrogram import Client, Filters

from config import cmds


@Client.on_message(Filters.command("save", prefixes=".") & Filters.me)
async def save(client, message):
    if message.reply_to_message:
        a = await message.reply_to_message.forward("me")
        if message.text.split(' ', 1)[1]:
            await a.reply(message.text.split(' ', 1)[1])
    elif message.text.split(' ', 1)[1]:
        await client.send_message(message.from_user.id, message.text.split(' ', 1)[1])
    await message.edit('saved')

cmds.update({'.save':'Save a message'})
