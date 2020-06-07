from config import sudoers
from pyrogram import Client, Filters

@Client.on_message(Filters.su_cmd(r'^\Whelp'))
async def on_settings(client, message):
    lang = message.lang
    keyboard = [
        [(lang.about_userlixo, 'settings_about_userlixo')],
        [(lang.commands, 'settings_commands'), (lang.plugins, 'settings_plugins')],
        [(lang.chat, 'https://t.me/AmanoChat', 'url'), (lang.channel, 'https://t.me/AmanoTeam', 'url')]
    ]
    await message.reply(lang.help_text, keyboard)