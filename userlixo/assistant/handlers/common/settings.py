from langs import Langs
from pyrogram.helpers import ikb


def compose_settings_message(lang: Langs, append_back: bool = True):
    lines = [
        [(lang.language, "setting_language")],
        [(lang.sudoers, "setting_sudoers")],
        [(lang.env_vars, "setting_env")],
    ]
    if append_back:
        lines.append([(lang.back, "start")])
        
    keyboard = ikb(lines)
    text = lang.settings_text

    return text, keyboard
