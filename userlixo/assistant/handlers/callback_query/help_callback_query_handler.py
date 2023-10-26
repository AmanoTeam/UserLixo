from kink import inject

from userlixo.assistant.handlers.abstract import CallbackQueryHandler
from userlixo.assistant.handlers.common.help import compose_help_message


@inject
class HelpCallbackQueryHandler(CallbackQueryHandler):
    def __init__(self, language_selector):
        self.get_lang = language_selector.get_lang

    async def handle_callback_query(self, _c, m):
        lang = self.get_lang()

        text, keyboard = compose_help_message(lang)
        await m.message.edit(text, reply_markup=keyboard)
