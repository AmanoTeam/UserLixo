from pyrogram import Client, Filters

@Client.on_message(Filters.command("doc", prefixes=".") & Filters.me)
def doc(client, message):
    doc = message.text.split(' ',1)[1]
    client.send_document(message.chat.id, doc)
    message.delete()