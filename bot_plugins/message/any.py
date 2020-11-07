import os
from config import langs
from database import Config
from pyrogram import Client, filters

# Getting the language to use
@Client.on_message(group=-2)
async def deflang(client, message):
    message.lang = langs.get_language(os.getenv('LANGUAGE'))

@Client.on_message(~filters.sudoers | filters.edited)
async def to_reject(client, message):
    message.stop_propagation()