import os
from userlixo.config import langs
from userlixo.database import Config
from pyrogram import Client, filters

# Getting the language to use
@Client.on_message(group=-2)
async def deflang(client, message):
    message._lang = langs.get_language(os.getenv('LANGUAGE'))

# Define what updates to reject
@Client.on_message(filters.edited)
async def reject(client, message):
    message.stop_propagation()