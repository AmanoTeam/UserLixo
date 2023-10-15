from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message

from userlixo.handlers.bot.upgrade import on_upgrade_u


@Client.on_message(filters.web_data_cmd("upgrade"))
async def upgrade(c: Client, m: Message):
    await on_upgrade_u(c, m)
