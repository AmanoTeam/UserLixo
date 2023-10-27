from abc import ABC, abstractmethod

from pyrogram import Client
from pyrogram.types import Message


class MessageHandler(ABC):
    @abstractmethod
    async def handle_message(self, client: Client, message: Message):
        pass
