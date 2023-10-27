from collections.abc import Callable

from pyrogram.filters import Filter


def on_message(filters: Filter = None, group: int = 0) -> Callable:
    def decorator(func: Callable) -> Callable:
        func.on = "message"
        func.filters = filters
        func.group = group

        return func

    return decorator
