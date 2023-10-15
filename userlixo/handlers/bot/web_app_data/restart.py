from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message

from userlixo.handlers.bot.restart import on_restart_u


@Client.on_message(filters.web_data_cmd("restart"))
async def restart(c: Client, m: Message):
    await on_restart_u(c, m)
