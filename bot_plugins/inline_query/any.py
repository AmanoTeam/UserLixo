import os
from config import langs
from database import Config
from pyrogram import Client, Filters

# Getting the language to use
@Client.on_inline_query(group=-2)
async def deflang(client, query):
    query.lang = langs.get_language(os.getenv('LANGUAGE'))