from typing import Callable

from pyrogram.filters import Filter


def on_callback_query(filters: Filter = None, group: int = 0) -> Callable:
    def decorator(func: Callable) -> Callable:
        func.on = "callback_query"
        func.filters = filters
        func.group = group
        
        return func

    return decorator
