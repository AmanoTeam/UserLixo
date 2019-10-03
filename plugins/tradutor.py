from pyrogram import Client, Filters

@Client.on_message(Filters.command("tr", prefixes="!"))
def translater(client, message):
    pass