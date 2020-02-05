from pyrogram import Client, Filters


@Client.on_message(Filters.command(["tagall","tagalln"], prefixes=".") & Filters.me)
def tagall(client, message):
    message.delete()
    n = True
    b = message.text.split(' ', 1)
    a = b[1]
    if b[0] == '.tagalln':
        n = False
    for x in client.iter_chat_members(message.chat.id):
        if n and x.user.status == 'online':
            a += f"[‌](tg://user?id={x.user.id})"
    client.send_message(message.chat.id, a,reply_to_message_id=message.message_id)


@Client.on_message(Filters.command(["admin","adminn"], prefixes=".") & Filters.me)
def admin(client, message):
    message.delete()
    n = True
    b = message.text.split(' ', 1)
    a = b[1]
    if b[0] == '.adminn':
        n = False
    for x in client.iter_chat_members(message.chat.id, filter='administrators'):
        if n and x.user.status == 'online':
            a += f"[­](tg://user?id={x.user.id})"
    client.send_message(message.chat.id, a)
