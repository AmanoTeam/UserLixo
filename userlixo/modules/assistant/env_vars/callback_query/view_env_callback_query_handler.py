from kink import inject
from pyrogram.types import CallbackQuery

from userlixo.database import Config
from userlixo.modules.abstract import CallbackQueryHandler


@inject
class ViewEnvCallbackQueryHandler(CallbackQueryHandler):
    async def handle_callback_query(self, _client, query: CallbackQuery):
        key = query.matches[0]["key"]
        value = Config.get_or_none(Config.key == key).value
        await query.answer(value, show_alert=True)
