from typing import Callable

from pyrogram import Client
from pyrogram.filters import Filter


def on_message(filters: Filter = None, group: int = 0) -> Callable:
    def decorator(func: Callable) -> Callable:
        def register_handler(client: Client):
            client.on_message(filters, group)(func)

        func.register_handler = register_handler

        return func

    return decorator
