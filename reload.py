import contextlib

import hydrogram
from hydrogram import filters, types
from hydrogram.helpers import bki, ikb

from config import user
from db import Config, Message


async def query_edit(
    self, text: str, reply_markup=None, answer_kwargs={}, *args, **kwargs
):
    with contextlib.suppress(BaseException):
        await self.answer(**answer_kwargs)
    return await self.edit_message_text(
        text=text, reply_markup=reply_markup, *args, **kwargs
    )


def remove_keyboard(self, message_id=None, *args, **kwargs):
    return self._client.edit_message_reply_markup(
        self.chat.id, message_id or self.id, {}
    )


async def edit_text(self, text: str, reply_markup=None, *args, **kwargs):
    if isinstance(reply_markup, list):
        reply_markup = ikb(reply_markup)
    if self._client.me.id == self.from_user.id:
        return await self._client.edit_message_text(
            self.chat.id, self.id, text, reply_markup=reply_markup, **kwargs
        )
    else:
        return await self._client.send_message(
            self.chat.id, text, reply_markup=reply_markup, **kwargs, reply_to_message_id=self.id
        )


async def reply_text(self, text: str, reply_markup=None, *args, **kwargs):
    if not reply_markup or self._client.name == "bot":
        if type(reply_markup) == list:
            reply_markup = ikb(reply_markup)
        return await self._client.send_message(
            self.chat.id,
            text,
            reply_markup=reply_markup,
            reply_to_message_id=kwargs.get("reply_to_message_id", self.id),
            **{k: v for k, v in kwargs.items() if k != "reply_to_message_id"}
        )
    
    if not hasattr(self._client, 'assistant'):
        if type(reply_markup) == list:
            reply_markup = ikb(reply_markup)
        return await self._client.send_message(
            self.chat.id,
            text,
            reply_markup=reply_markup,
            reply_to_message_id=kwargs.get("reply_to_message_id", self.id),
            **{k: v for k, v in kwargs.items() if k != "reply_to_message_id"}
        )
    
    if type(reply_markup) == types.InlineKeyboardMarkup:
        reply_markup = bki(reply_markup)
    message = await Message.create(text=text, keyboard=reply_markup)
    bot = self._client.assistant

    reply_to = None
    if kwargs.get("reply_to_message_id"):
        reply_to = kwargs.get("reply_to_message_id")
    else:
        reply_to = self.id

    inline_results = await self._client.get_inline_bot_results(
        bot.me.username or bot.me.id, str(message.key)
    )
    result = inline_results.results[0]

    return await self._client.send_inline_bot_result(
        self.chat.id,
        inline_results.query_id,
        result.id,
        reply_to_message_id=reply_to,
    )


async def filter_sudoers_logic(flt, c, u):
    if not u.from_user:
        return None
    usr = u.from_user
    sudoers = (await Config.get(id="sudoers")).valuej
    return usr.id in sudoers or user.me.id == usr.id


async def main():
    original_reply = hydrogram.types.Message.reply
    
    async def smart_reply(self, *args, **kwargs):
        return await reply_text(self, *args, **kwargs)
    
    hydrogram.types.Message.reply = smart_reply
    hydrogram.types.CallbackQuery.edit = query_edit
    hydrogram.types.Message.remove_keyboard = remove_keyboard
    hydrogram.types.Message.edit = edit_text
    
    if not await Config.get_or_none(id="sudoers"):
        await Config.create(id="sudoers", valuej=[])


filter_sudoers = filters.create(filter_sudoers_logic, "FilterSudoers")
hydrogram.filters.sudoers = filter_sudoers
