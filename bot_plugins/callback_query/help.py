from pyrogram import Client, Filters
from pyromod.helpers import ikb

@Client.on_callback_query(Filters.su_regex('^help'))
async def on_settings(client, query):
    lang = query.lang
    keyboard = ikb([
        [(lang.about_userlixo, 'about_userlixo')],
        [(lang.commands, 'commands'), (lang.plugins, 'plugins')],
        [(lang.chat, 'https://t.me/AmanoChat', 'url'), (lang.channel, 'https://t.me/AmanoTeam', 'url')]
    ])
    await query.edit(lang.help_text, keyboard)