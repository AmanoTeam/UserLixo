# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

from pyrogram import types
from pyromod.helpers import bki, ikb

from userlixo.database import Message


async def query_edit(
    self, text: str, reply_markup=None, answer_kwargs={}, *args, **kwargs
):
    try:
        await self.answer(**answer_kwargs)
    except BaseException:
        pass
    edit = await self.edit_message_text(
        text=text, reply_markup=reply_markup, *args, **kwargs
    )
    return edit


def remove_keyboard(self, message_id=None, *args, **kwargs):
    return self._client.edit_message_reply_markup(
        self.chat.id, message_id or self.id, {}
    )


async def edit_text(self, text: str, reply_markup=None, *args, **kwargs):
    if type(reply_markup) == list:
        reply_markup = ikb(reply_markup)
    return await self._client.edit_message_text(
        self.chat.id, self.id, text, reply_markup=reply_markup, **kwargs
    )


async def reply_text(self, text: str, reply_markup=None, *args, **kwargs):
    if not reply_markup or self._client.name == "bot":
        return await self.reply_text(text, reply_markup=reply_markup, *args, **kwargs)
    if type(reply_markup) == types.InlineKeyboardMarkup:
        reply_markup = bki(reply_markup)
    message = await Message.create(text=text, keyboard=reply_markup)

    bot = self._client.assistant
    inline_results = await self._client.get_inline_bot_results(
        bot.me.username or bot.me.id, str(message.key)
    )
    result = inline_results.results[0]

    reply_to = None
    if kwargs.get("quote"):
        reply_to = self.id

    return await self._client.send_inline_bot_result(
        self.chat.id,
        inline_results.query_id,
        result.id,
        reply_to_message_id=reply_to,
    )
