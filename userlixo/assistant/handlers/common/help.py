from langs import Langs
from pyrogram.helpers import ikb


def compose_help_message(lang: Langs):
    keyboard = ikb([
        [(lang.about_userlixo, "about_userlixo")],
        [(lang.commands, "about_commands"), (lang.plugins, "about_plugins")],
        [
            (lang.chat, "https://t.me/UserLixoChat", "url"),
            (lang.channel, "https://t.me/UserLixo", "url"),
        ],
    ])
    text = lang.help_text
    return text, keyboard
