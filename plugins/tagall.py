from pyrogram import Client, Filters


@Client.on_message(Filters.command("tagall", prefixes=".") & Filters.me)
async def tagall(client, message):
    await message.delete()
    a = message.text.split(' ', 1)[1] or ''
    async for x in client.iter_chat_members(message.chat.id):
        if x.user.status == 'online':
            a += f"[‌](tg://user?id={x.user.id})"
    await client.send_message(message.chat.id, a)


@Client.on_message(Filters.command("admin", prefixes=".") & Filters.me)
async def admin(client, message):
    await message.delete()
    a = message.text.split(' ', 1)[1] or ''
    async for x in client.iter_chat_members(message.chat.id, filter='administrators'):
        if x.user.status == 'online':
            a += f"[­](tg://user?id={x.user.id})"
    await client.send_message(message.chat.id, a)
