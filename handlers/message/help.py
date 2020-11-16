from config import sudoers
from pyrogram import Client, filters

@Client.on_message(filters.su_cmd('help'))
async def on_settings(c, m):
    lang = m.lang
    keyboard = [
        [(lang.about_userlixo, 'about_userlixo')],
        [(lang.commands, 'list_commands 0'), (lang.plugins, 'list_plugins 0')],
        [(lang.chat, 'https://t.me/AmanoChat', 'url'), (lang.channel, 'https://t.me/AmanoTeam', 'url')]
    ]
    await m.reply(lang.help_text, keyboard)