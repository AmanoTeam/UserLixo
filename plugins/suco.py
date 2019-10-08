from pyrogram import Client, Filters
from config import sudos

@Client.on_message(Filters.command("suco", prefixes=["/","!"]))
def suco(client, message):
    if message.from_user.id in sudos:
        message.reply('✅🍹')
    else:
        message.reply('❌🍹')