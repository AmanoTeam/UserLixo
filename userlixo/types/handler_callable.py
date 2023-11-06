from collections.abc import Callable

from pyrogram.handlers.handler import Handler


class HandlerCallable(Callable):
    handlers: list[tuple[Handler, int]]
