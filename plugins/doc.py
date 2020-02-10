from pyrogram import Client, Filters


@Client.on_message(Filters.command("doc", prefixes=".") & Filters.me)
async def doc(client, message):
    docf = message.text.split(' ', 1)[1]
    await client.send_document(message.chat.id, docf)
    await message.delete()
