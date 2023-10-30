from kink import inject
from pyrogram.helpers import ikb
from pyrogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

from userlixo.database import Message
from userlixo.modules.abstract import InlineQueryHandler


@inject
class IndexInlineQueryHandler(InlineQueryHandler):
    async def handle_inline_query(self, _c, iq: InlineQuery):
        index = int(iq.matches[0]["index"])
        message = await Message.get_or_none(key=index)
        if not message:
            results = [
                InlineQueryResultArticle(
                    title="undefined index",
                    input_message_content=InputTextMessageContent(f"Undefined index {index}"),
                )
            ]
            return await iq.answer(results, cache_time=0)

        keyboard = ikb(message.keyboard)
        text = message.text

        results = [
            InlineQueryResultArticle(
                title="index",
                input_message_content=InputTextMessageContent(text, disable_web_page_preview=True),
                reply_markup=keyboard,
            )
        ]

        await iq.answer(results, cache_time=0)
        await (await Message.get(key=message.key)).delete()
        return None
