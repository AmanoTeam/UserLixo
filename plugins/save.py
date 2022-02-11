from pyrogram import Client, filters
from pyrogram.types import Message

from config import cmds


@Client.on_message(filters.command("save", prefixes=".") & filters.me)
async def save(client: Client, message: Message):
    if message.reply_to_message:
        a = await message.reply_to_message.forward("me")
        if message.text.split(" ", 1)[1]:
            await a.reply(message.text.split(" ", 1)[1])
    elif message.text.split(" ", 1)[1]:
        await client.send_message(message.from_user.id, message.text.split(" ", 1)[1])
    await message.edit("saved")


cmds.update({".save": "Save a message"})
