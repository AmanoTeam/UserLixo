from abc import ABC, abstractmethod

from hydrogram import Client
from hydrogram.types import CallbackQuery


class CallbackQueryHandler(ABC):
    @abstractmethod
    async def handle_callback_query(self, client: Client, query: CallbackQuery):
        pass
