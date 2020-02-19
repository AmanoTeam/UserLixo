from pyrogram import Client, Filters

from config import cmds


@Client.on_message(Filters.command("doc", prefixes=".") & Filters.me)
async def doc(client, message):
    docf = message.text.split(' ', 1)[1]
    await client.send_document(message.chat.id, docf)
    await message.delete()


cmds.update({'.doc':'Uploads a locally stored file to the chat'})
