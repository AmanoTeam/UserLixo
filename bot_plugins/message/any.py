import os
from config import langs
from database import Config
from pyrogram import Client, Filters

# Getting the language to use
@Client.on_message(group=-2)
async def deflang(client, message):
    message.lang = langs.get_language(os.getenv('LANGUAGE'))

@Client.on_message(~Filters.sudoers | Filters.edited)
async def to_reject(client, message):
    message.stop_propagation()