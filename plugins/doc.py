from pyrogram import Client, filters
from pyrogram.types import Message

from config import cmds


@Client.on_message(filters.command("doc", prefixes=".") & filters.me)
async def doc(client: Client, message: Message):
    docf = message.text.split(" ", 1)[1]
    await client.send_document(message.chat.id, docf)
    await message.delete()


cmds.update({".doc": "Uploads a locally stored file to the chat"})
