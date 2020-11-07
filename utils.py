from database import Message
from pyrogram import filters

info = {"user": {}, "bot": {}}

def tryint(value):
    try:
        return int(value)
    except:
        return value

# Pyrogram monkeypatch
async def query_edit(self, text, reply_markup, answer_kwargs={}, *args, **kwargs):
    answer = await self.answer(**answer_kwargs)
    edit = await self.edit_message_text(text=text, reply_markup=reply_markup, *args, **kwargs)
    return edit#, answer

def remove_keyboard(self, message_id = None, *args, **kwargs):
    return self._client.edit_message_reply_markup(self.chat.id, message_id or self.message_id, {})

async def reply_text(self, text: str, reply_markup=None, *args, **kwargs):
    if reply_markup and not self._client.bot_token:
        message = await Message.create(text=text, keyboard=reply_markup)
        inline_results = await self._client.get_inline_bot_results(info['bot'].username or info['bot'].id, str(message.key))
        result = inline_results.results[0]
        return await self._client.send_inline_bot_result(self.chat.id, inline_results.query_id, result.id, **kwargs)
    return await self.reply_text(text, reply_markup=reply_markup, *args, **kwargs)
