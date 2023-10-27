from kink import inject
from pyrogram import Client
from pyrogram.helpers import ikb
from pyrogram.types import CallbackQuery, Message

from userlixo.assistant.handlers.abstract import CallbackQueryHandler, MessageHandler
from userlixo.services.language_selector import LanguageSelector


@inject
class StartHandler(MessageHandler, CallbackQueryHandler):
    def __init__(self, language_selector: LanguageSelector):
        self.get_lang = language_selector.get_lang

    async def handle_message(self, _c: Client, m: Message):
        text, keyboard = self.compose_message(_c, m)
        await m.reply(text, reply_markup=keyboard, quote=True)

    async def handle_callback_query(self, _c: Client, cq: CallbackQuery):
        text, keyboard = self.compose_message(_c, cq)
        await cq.edit_message_text(text, reply_markup=keyboard)

    def compose_message(self, _c: Client, u: Message | CallbackQuery):
        lang = self.get_lang()

        keyboard = ikb(
            [
                [(lang.upgrade, "upgrade"), [lang.restart, "restart"]],
                [(lang.commands, "list_commands 0"), (lang.plugins, "list_plugins")],
                [(lang.help, "help"), (lang.settings, "settings")],
            ]
        )

        text = lang.start_text

        return text, keyboard
