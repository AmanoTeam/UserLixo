from config import sudoers
from pyrogram import Client, filters

@Client.on_message(filters.su_cmd('help'))
async def on_settings(client, message):
    lang = message.lang
    keyboard = [
        [(lang.about_userlixo, 'about_userlixo')],
        [(lang.commands, 'commands'), (lang.plugins, 'plugins')],
        [(lang.chat, 'https://t.me/AmanoChat', 'url'), (lang.channel, 'https://t.me/AmanoTeam', 'url')]
    ]
    await message.reply(lang.help_text, keyboard)