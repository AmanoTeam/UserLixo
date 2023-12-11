import contextlib

from pyrogram import types, filters
from pyrogram.helpers import bki, ikb
import pyrogram
from db import Message, Config
from config import user

async def query_edit(self, text: str, reply_markup=None, answer_kwargs={}, *args, **kwargs):
    with contextlib.suppress(BaseException):
        await self.answer(**answer_kwargs)
    return await self.edit_message_text(text=text, reply_markup=reply_markup, *args, **kwargs)


def remove_keyboard(self, message_id=None, *args, **kwargs):
    return self._client.edit_message_reply_markup(self.chat.id, message_id or self.id, {})


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
    if kwargs.get("reply_to_message_id"):
        reply_to = kwargs.get("reply_to_message_id")
    else:
        reply_to = self.id

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
    pyrogram.types.CallbackQuery.edit = query_edit
    pyrogram.types.Message.remove_keyboard = remove_keyboard
    pyrogram.types.Message.reply = reply_text
    pyrogram.types.Message.edit = edit_text
    if not await Config.get_or_none(id="sudoers"):
        await Config.create(id="sudoers", valuej=[])

filter_sudoers = filters.create(filter_sudoers_logic, "FilterSudoers")
pyrogram.filters.sudoers = filter_sudoers