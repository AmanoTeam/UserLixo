from pyrogram import Client, Filters


@Client.on_message(Filters.command("doc", prefixes=".") & Filters.me)
def doc(client, message):
    docf = message.text.split(' ', 1)[1]
    client.send_document(message.chat.id, docf)
    message.delete()
