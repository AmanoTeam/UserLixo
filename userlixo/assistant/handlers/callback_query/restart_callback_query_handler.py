from kink import inject
from pyrogram.types import Message

from userlixo.assistant.handlers.abstract import CallbackQueryHandler
from userlixo.assistant.handlers.common.restart import compose_before_restart_message, save_before_restart_message_info, \
    self_restart_process


@inject
class RestartCallbackQueryHandler(CallbackQueryHandler):
    def __init__(self, language_selector):
        self.get_lang = language_selector.get_lang

    async def handle_callback_query(self, _c, m: Message):
        lang = self.get_lang()

        text = compose_before_restart_message(lang)
        msg = await m.edit(text)

        await save_before_restart_message_info(
            msg.id,
            msg.chat.id,
            "bot"
        )

        self_restart_process()
