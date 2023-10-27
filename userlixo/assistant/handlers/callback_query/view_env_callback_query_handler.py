from kink import inject
from pyrogram.types import CallbackQuery

from userlixo.assistant.handlers.abstract import CallbackQueryHandler
from userlixo.database import Config


@inject
class ViewEnvCallbackQueryHandler(CallbackQueryHandler):
    async def handle_callback_query(self, _client, query: CallbackQuery):
        key = query.matches[0]["key"]
        value = (await Config.get_or_none(key=key)).value
        await query.answer(value, show_alert=True)
