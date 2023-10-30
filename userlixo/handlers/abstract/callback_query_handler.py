from abc import ABC, abstractmethod

from pyrogram import Client
from pyrogram.types import CallbackQuery


class CallbackQueryHandler(ABC):
    @abstractmethod
    async def handle_callback_query(self, client: Client, query: CallbackQuery):
        pass
