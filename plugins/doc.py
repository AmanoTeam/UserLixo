from pyrogram import Client, Filters
from config import sudos

@Client.on_message(Filters.command("doc", prefixes="!"))
def doc(client, message):
    if message.from_user.id in sudos:
        doc = message.text.split(' ',1)[1]
        message.reply_document(doc)