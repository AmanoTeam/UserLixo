from config import sudoers
from database import Message
from pyrogram import Client, filters
from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent
from pyromod.helpers import ikb

@Client.on_inline_query(filters.sudoers & filters.regex('^(?P<index>\d+)'))
async def on_index(client, query):
    index = int(query.matches[0]['index'])
    message = await Message.get_or_none(key=index)
    if not message:
        results = [
            InlineQueryResultArticle(title="undefined index", input_message_content=InputTextMessageContent(f"Undefined index {index}"))
        ]
        return await query.answer(results, cache_time=0)
    
    keyboard = ikb(message.keyboard)
    text = message.text
    
    results = [
        InlineQueryResultArticle(title="index", input_message_content=InputTextMessageContent(text, disable_web_page_preview=True), reply_markup=keyboard)
    ]
    
    await query.answer(results, cache_time=0)
    await Message.get(key=message.key).delete()