from pyrogram import Client, Filters

@Client.on_message(Filters.command("tr", prefix="!"))
def translater(client, message):
    pass