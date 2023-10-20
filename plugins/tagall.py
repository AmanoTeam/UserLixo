import html

from pyrogram import Client, filters
from pyrogram.types import Message

from config import cmds

char = html.unescape("&#8204;")


@Client.on_message(filters.command("tagall", prefixes=".") & filters.me)
async def tagall(client: Client, message: Message):
    await message.delete()

    splitted = message.text.split(" ", 1)
    if len(splitted) < 2:
        a = ""
    else:
        a = splitted[1]

    async for x in client.get_chat_members(message.chat.id):
        if x.user.status == "online":
            a += f"[{char}](tg://user?id={x.user.id})"
    kwargs = {}
    if message.reply_to_message:
        kwargs["reply_to_message_id"] = message.reply_to_message.id
    await client.send_message(message.chat.id, a, **kwargs)


@Client.on_message(filters.command("ftagall", prefixes=".") & filters.me)
async def ftagall(client: Client, message: Message):
    await message.delete()

    splitted = message.text.split(" ", 1)
    if len(splitted) < 2:
        a = ""
    else:
        a = splitted[1]

    async for x in client.get_chat_members(message.chat.id):
        if x.user.is_bot == False and x.user.is_deleted == False:
            a += f"[{char}](tg://user?id={x.user.id})"
    kwargs = {}
    if message.reply_to_message:
        kwargs["reply_to_message_id"] = message.reply_to_message.id
    await client.send_message(message.chat.id, a, **kwargs)


@Client.on_message(filters.command("admin", prefixes=".") & filters.me)
async def admin(client: Client, message: Message):
    await message.delete()

    splitted = message.text.split(" ", 1)
    if len(splitted) < 2:
        a = "@admin"
    else:
        a = splitted[1]

    async for x in client.iter_chat_members(message.chat.id, filter="administrators"):
        if x.user.status == "online":
            a += f"[{char}](tg://user?id={x.user.id})"
    kwargs = {}
    if message.reply_to_message:
        kwargs["reply_to_message_id"] = message.reply_to_message.id
    await client.send_message(message.chat.id, a, **kwargs)


@Client.on_message(filters.command("fadmin", prefixes=".") & filters.me)
async def fadmin(client: Client, message: Message):
    await message.delete()

    splitted = message.text.split(" ", 1)
    if len(splitted) < 2:
        a = "@admin"
    else:
        a = splitted[1]

    async for x in client.iter_chat_members(message.chat.id, filter="administrators"):
        if x.user.is_bot == False and x.user.is_deleted == False:
            a += f"[{char}](tg://user?id={x.user.id})"

    kwargs = {}
    if message.reply_to_message:
        kwargs["reply_to_message_id"] = message.reply_to_message.id
    await client.send_message(message.chat.id, a, **kwargs)


cmds.update(
    {
        ".tagall": "Mark all online members of the group",
        ".ftagall": "Mark all members of the group",
        ".admin": "Mark all online admins of the group",
        ".fadmin": "Mark all admins of the group",
    }
)