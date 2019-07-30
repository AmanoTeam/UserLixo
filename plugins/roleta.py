from pyrogram import Client, Filters
import random

@Client.on_message(Filters.command("roleta", prefix = ['!','/'], separator = '.'))
def roleta(client, message):
    if message.chat.id == -1001388201593:
        res = random.choice(['Bam', 'passou', 'passou', 'passou', 'passou', 'passou'])
        message.reply(res)
        if res == 'Bam':
            client.kick_chat_member(message.chat.id,message.from_user.id)
            client.unban_chat_member(message.chat.id,message.from_user.id)