from dataclasses import dataclass
from datetime import datetime

from kink import inject

from userlixo.modules.abstract import CallbackQueryHandler
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class PingCallbackQueryHandler(CallbackQueryHandler):
    language_selector: LanguageSelector

    async def handle_callback_query(self, c, cq):
        before = datetime.now()
        await c.get_me()
        after = datetime.now()
        diff_ms = (after - before).microseconds / 1000

        await cq.answer(f"Pong! {diff_ms}ms", show_alert=True)
