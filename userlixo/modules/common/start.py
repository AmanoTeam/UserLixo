from langs import Langs
from pyrogram.helpers import ikb


def compose_start_message(lang: Langs):
    keyboard = ikb(
        [
            [(lang.upgrade, "upgrade"), [lang.restart, "restart"]],
            [(lang.commands, "list_commands 0"), (lang.plugins, "list_plugins 0")],
            [(lang.help, "help"), (lang.settings, "settings")],
        ]
    )

    text = lang.start_text
    return text, keyboard
