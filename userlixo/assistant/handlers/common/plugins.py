from langs import Langs
from pyrogram.helpers import ikb

from userlixo.config import user, bot


def compose_list_plugins_message(lang: Langs, append_back: bool = False):
    text = lang.list_plugins_select_type(
        user=("@" + user.me.username if user.me.username else user.me.first_name),
        bot=bot.me.username,
    )
    keyboard = ikb(
        [
            [
                (lang.user_plugins, "user_plugins 0"),
                (lang.bot_plugins, "bot_plugins 0"),
            ],
            [(lang.back, "start")] if append_back else [],
        ]
    )

    return text, keyboard
