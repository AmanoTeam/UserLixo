from hydrogram.types import CallbackQuery
from kink import inject

from userlixo.database import Config
from userlixo.modules.abstract import CallbackQueryHandler


@inject
class ViewEnvCallbackQueryHandler(CallbackQueryHandler):
    @staticmethod
    async def handle_callback_query(_client, query: CallbackQuery):
        key = query.matches[0]["key"]
        value = Config.get_or_none(Config.key == key).value
        await query.answer(value, show_alert=True)
