from pyrogram import Client, Filters
import dicioinformal

@Client.on_message(Filters.command("dicio", prefixes=".") & Filters.me)
def dicio(client, message):
    txt = message.text.split(' ',1)[1]
    a = dicioinformal.definicao(txt)['results']
    if a:
        frase = f'{a[0]["title"]}:\n{a[0]["tit"]}\n\n__{a[0]["desc"]}__'
    else:
        frase = 'sem resultado'
    message.edit(frase)
