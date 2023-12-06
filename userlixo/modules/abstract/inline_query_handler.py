from abc import ABC, abstractmethod

from hydrogram import Client
from hydrogram.types import InlineQuery


class InlineQueryHandler(ABC):
    @abstractmethod
    async def handle_inline_query(self, client: Client, query: InlineQuery):
        pass
