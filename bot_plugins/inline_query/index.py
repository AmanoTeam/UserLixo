from config import sudoers
from database import Message
from pyrogram import Client, Filters, InlineQueryResultArticle, InputTextMessageContent
from pyromod.helpers import ikb

@Client.on_inline_query(Filters.regex('^\d+') & Filters.sudoers)
async def on_index(client, query):
    index = int(query.matches[0][0])
    message = await Message.get_or_none(key=index)
    if not message:
        results = [
            InlineQueryResultArticle(title="undefined index", input_message_content=InputTextMessageContent(f"Undefined index {index}"))
        ]
        return await query.answer(results, is_personal=True)
    
    keyboard = ikb(message.keyboard)
    text = message.text
    
    results = [
        InlineQueryResultArticle(title="index", input_message_content=InputTextMessageContent(text), reply_markup=keyboard)
    ]
    
    await query.answer(results, is_personal=True)
    await Message.get(key=message.key).delete()