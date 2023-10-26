from kink import inject

from userlixo.assistant.handlers.abstract import MessageHandler
from userlixo.assistant.handlers.common.help import compose_help_message


@inject
class HelpMessageHandler(MessageHandler):
    def __init__(self, language_selector):
        self.get_lang = language_selector.get_lang

    async def handle_message(self, _c, m):
        lang = self.get_lang()

        text, keyboard = compose_help_message(lang)
        await m.reply(text, reply_markup=keyboard, quote=True)
