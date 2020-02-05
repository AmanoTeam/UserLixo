from pyrogram import Client, Filters


@Client.on_message(Filters.command("tagall", prefixes=".") & Filters.me)
def tagall(client, message):
    message.delete()
    a = message.text.split(' ', 1)[1] or ''
    for x in client.iter_chat_members(message.chat.id):
        if x.user.status == 'online':
            a += f"[‌](tg://user?id={x.user.id})"
    client.send_message(message.chat.id, a,reply_to_message_id=message.message_id)


@Client.on_message(Filters.command("admin", prefixes=".") & Filters.me)
def admin(client, message):
    message.delete()
    a = message.text.split(' ', 1)[1] or ''
    for x in client.iter_chat_members(message.chat.id, filter='administrators'):
        if x.user.status == 'online':
            a += f"[­](tg://user?id={x.user.id})"
    client.send_message(message.chat.id, a)
