from collections.abc import Callable

from hydrogram.handlers.handler import Handler


class HandlerCallable(Callable):
    handlers: list[tuple[Handler, int]]
