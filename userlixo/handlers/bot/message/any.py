import os
from userlixo.config import langs
from userlixo.database import Config
from pyrogram import Client, filters

# Getting the language to use
@Client.on_message(group=-2)
async def deflang(c, m):
    m._lang = langs.get_language(os.getenv('LANGUAGE'))

@Client.on_message(~filters.sudoers | filters.edited)
async def to_reject(c, m):
    m.stop_propagation()