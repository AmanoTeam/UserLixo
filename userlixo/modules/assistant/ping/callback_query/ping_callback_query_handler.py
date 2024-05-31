from dataclasses import dataclass
from datetime import UTC, datetime

from kink import inject

from userlixo.modules.abstract import CallbackQueryHandler
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class PingCallbackQueryHandler(CallbackQueryHandler):
    language_selector: LanguageSelector

    @staticmethod
    async def handle_callback_query(c, cq):
        before = datetime.now(tz=UTC)
        await c.get_me()
        after = datetime.now(tz=UTC)
        diff_ms = (after - before).microseconds / 1000

        await cq.answer(f"Pong! {diff_ms}ms", show_alert=True)
