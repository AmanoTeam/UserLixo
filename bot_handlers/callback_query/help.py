from pyrogram import Client, filters
from pyromod.helpers import ikb

@Client.on_callback_query(filters.sudoers & filters.regex('^help'))
async def on_settings(client, query):
    lang = query.lang
    keyboard = [
        [(lang.about_userlixo, 'about_userlixo')],
        [(lang.commands, 'list_commands 0'), (lang.plugins, 'list_plugins 0')],
        [(lang.chat, 'https://t.me/AmanoChat', 'url'), (lang.channel, 'https://t.me/AmanoTeam', 'url')]
    ]
    if query.data.endswith('start'):
        keyboard.append([ (lang.back, 'start') ])
    keyboard = ikb(keyboard)
    await query.edit(lang.help_text, keyboard)