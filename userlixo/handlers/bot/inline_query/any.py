import os
from userlixo.config import langs
from userlixo.database import Config
from pyrogram import Client, filters

# Getting the language to use
@Client.on_inline_query(group=-2)
async def deflang(c, iq):
    iq._lang = langs.get_language(os.getenv('LANGUAGE'))