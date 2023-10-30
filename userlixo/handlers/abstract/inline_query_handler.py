from abc import ABC, abstractmethod

from pyrogram import Client
from pyrogram.types import InlineQuery


class InlineQueryHandler(ABC):
    @abstractmethod
    async def handle_inline_query(self, client: Client, query: InlineQuery):
        pass
