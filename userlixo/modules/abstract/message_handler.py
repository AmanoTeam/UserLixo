from abc import ABC, abstractmethod

from hydrogram import Client
from hydrogram.types import Message


class MessageHandler(ABC):
    @abstractmethod
    async def handle_message(self, client: Client, message: Message):
        pass
