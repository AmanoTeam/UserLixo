from langs import Langs
from pyrogram.helpers import ikb


def compose_settings_message(lang: Langs, append_back: bool = True):
    keyboard = ikb([
        [(lang.language, "setting_language")],
        [(lang.sudoers, "setting_sudoers")],
        [(lang.env_vars, "setting_env")],
        [(lang.back, "start")] if append_back else []
    ])
    text = lang.settings_text

    return text, keyboard
