import logging
from dataclasses import dataclass

from kink import inject
from pyrogram import filters
from pyrogram.errors import ListenerStopped
from pyrogram.helpers import ikb
from pyrogram.types import CallbackQuery

from userlixo.database import Config
from userlixo.modules.abstract import CallbackQueryHandler
from userlixo.utils.services.language_selector import LanguageSelector

logger = logging.getLogger(__name__)


@inject
@dataclass
class EditEnvCallbackQueryHandler(CallbackQueryHandler):
    language_selector: LanguageSelector

    async def handle_callback_query(self, _client, query: CallbackQuery):
        lang = self.language_selector.get_lang()

        key = query.matches[0]["key"]
        value = (await Config.get_or_none(key=key)).value

        text = lang.edit_env_text(key=key, value=value)
        keyboard = ikb([[(lang.back, "setting_env")]])
        last_msg = await query.edit(text, keyboard)

        env_requires_restart = ["PREFIXES", "DATABASE_URL", "BOT_TOKEN"]
        try:
            while True:
                user_id = query.from_user.id
                msg = await query.from_user.listen(chat_id=user_id, filters=filters.text)
                await last_msg.remove_keyboard()
                await Config.get(key=key).update(value=msg.text)
                if key in env_requires_restart:
                    text = lang.edit_env_text_restart(key=key, value=msg.text)
                    keyboard = ikb(
                        [
                            [(lang.restart_now, "restart_now")],
                            [(lang.back, "setting_env")],
                        ]
                    )
                else:
                    text = lang.edit_env_text(key=key, value=msg.text)
                    keyboard = ikb([[(lang.back, "setting_env")]])
                last_msg = await msg.reply_text(text, reply_markup=keyboard)
        except ListenerStopped:
            logger.debug("Stopped listening for message in EditEnvCallbackQueryHandler")
        except Exception as e:
            logger.exception(e)
