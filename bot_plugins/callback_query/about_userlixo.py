from pyrogram import Client, Filters
from pyromod.helpers import ikb

@Client.on_callback_query(Filters.su_regex('^about_userlixo'))
async def on_about_userlixo(client, query):
    lang = query.lang
    keyboard = ikb([
        [(lang.back, 'help')]
    ])
    await query.edit(lang.about_userlixo_text, keyboard)