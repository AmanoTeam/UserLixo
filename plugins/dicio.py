from pyrogram import Client, Filters
import dicioinformal

@Client.on_message(Filters.command("dicio", prefixes="/"))
def dicio(client, message):
    txt = message.text.split(' ',1)[1]
    a = dicioinformal.definicao(txt)
    message.reply(a)
