from abc import ABC, abstractmethod

from hydrogram import Client
from hydrogram.types import Message


class WebAppDataHandler(ABC):
    @abstractmethod
    async def handle_web_app_data(self, client: Client, message: Message):
        pass
