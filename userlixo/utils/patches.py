# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

import contextlib
from enum import Enum

from pyrogram import types
from pyrogram.helpers import bki, ikb

from userlixo.database import Message


async def query_edit(self, text: str, reply_markup=None, answer_kwargs={}, *args, **kwargs):
    with contextlib.suppress(BaseException):
        await self.answer(**answer_kwargs)
    return await self.edit_message_text(text=text, reply_markup=reply_markup, *args, **kwargs)


def remove_keyboard(self, message_id=None, *args, **kwargs):
    return self._client.edit_message_reply_markup(self.chat.id, message_id or self.id, {})


async def edit_text(self, text: str, reply_markup=None, *args, **kwargs):
    if isinstance(reply_markup, list):
        reply_markup = ikb(reply_markup)
    return await self._client.edit_message_text(
        self.chat.id, self.id, text, reply_markup=reply_markup, **kwargs
    )


class MessageTypes(Enum):
    NORMAL = "NORMAL"
    TOPIC = "TOPIC"
    REPLY_IN_TOPIC = "REPLY_IN_TOPIC"


def get_message_type(message):
    is_reply_to_top_message_id_none = message.reply_to_top_message_id is None
    is_reply_to_message_id_none = message.reply_to_message_id is None

    if is_reply_to_top_message_id_none and is_reply_to_message_id_none:
        message_type = MessageTypes.NORMAL
    elif is_reply_to_top_message_id_none and not is_reply_to_message_id_none:
        message_type = MessageTypes.TOPIC
    elif not is_reply_to_top_message_id_none and not is_reply_to_message_id_none:
        message_type = MessageTypes.REPLY_IN_TOPIC
    else:
        data = (
            f"reply_to_top_message_id: {message.reply_to_top_message_id} and"
            " reply_to_message_id: {self.reply_to_message_id}"
        )
        raise ValueError("Message type not found: " + data)

    return message_type


def get_proper_reply_id(message, quote=True):
    message_type = get_message_type(message)

    reply_to = None
    if message_type == MessageTypes.NORMAL and quote:
        reply_to = message.id
    elif message_type == MessageTypes.TOPIC:
        reply_to = message.reply_to_message_id
        if quote:
            reply_to = message.id
    elif message_type == MessageTypes.REPLY_IN_TOPIC:
        reply_to = message.reply_to_top_message_id
        if quote:
            reply_to = message.reply_to_message_id

    return reply_to


async def reply_text(self, text: str, reply_markup=None, *args, **kwargs):
    reply_to = get_proper_reply_id(self, quote=kwargs.get("quote", False))

    if not reply_markup or self._client.name == "bot":
        if "reply_to_message_id" in kwargs:
            del kwargs["reply_to_message_id"]
        return await self.reply_text(
            text, *args, reply_markup=reply_markup, reply_to_message_id=reply_to, **kwargs
        )
    if type(reply_markup) == types.InlineKeyboardMarkup:
        reply_markup = bki(reply_markup)
    message = await Message.create(text=text, keyboard=reply_markup)

    bot = self._client.assistant
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
