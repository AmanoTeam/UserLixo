from pyrogram import Client, Filters


@Client.on_message(Filters.command("tagall", prefixes=".") & Filters.me)
def tagall(client, message):
    a = message.text.split(' ', 1)[1] or ''
    for x in client.iter_chat_members(message.chat.id):
        if x.user.status == 'online':
            a += f"\n[{x.user.first_name}](tg://user?id={x.user.id})"
    message.edit(a)


@Client.on_message(Filters.command("admin", prefixes=".") & Filters.me)
def admin(client, message):
    a = message.text.split(' ', 1)[1] or ''
    for x in client.iter_chat_members(message.chat.id, filter='administrators'):
        if x.user.status == 'online':
            a += f"\n[{x.user.first_name}](tg://user?id={x.user.id})"
    message.edit(a)
