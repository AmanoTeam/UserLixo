from pyrogram import Client, Filters


@Client.on_message(Filters.command("save", prefixes=".") & Filters.me)
def save(client, message):
    if message.reply_to_message:
        a = message.reply_to_message.forward("me")
        if message.text.split(' ', 1)[1]:
            a.reply(message.text.split(' ', 1)[1])
    elif message.text.split(' ', 1)[1]:
        client.send_message(message.from_user.id, message.text.split(' ', 1)[1])
    message.edit('saved')
