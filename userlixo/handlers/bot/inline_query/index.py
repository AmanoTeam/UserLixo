from userlixo.config import sudoers
from userlixo.database import Message
from pyrogram import Client, filters
from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent
from pyromod.helpers import ikb

@Client.on_inline_query(filters.sudoers & filters.regex('^(?P<index>\d+)'))
async def on_index(c, iq):
    index = int(iq.matches[0]['index'])
    message = await Message.get_or_none(key=index)
    if not message:
        results = [
            InlineQueryResultArticle(title="undefined index", input_message_content=InputTextMessageContent(f"Undefined index {index}"))
        ]
        return await iq.answer(results, cache_time=0)
    
    keyboard = ikb(message.keyboard)
    text = message.text
    
    results = [
        InlineQueryResultArticle(title="index", input_message_content=InputTextMessageContent(text, disable_web_page_preview=True), reply_markup=keyboard)
    ]
    
    await iq.answer(results, cache_time=0)
    await Message.get(key=message.key).delete()