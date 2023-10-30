from collections.abc import Callable

from pyrogram.filters import Filter

from userlixo.config import filter_sudoers


def on_callback_query(
    filters: Filter = None, group: int = 0, sudoers_only: bool = True
) -> Callable:
    def decorator(func: Callable) -> Callable:
        func.on = "callback_query"
        func.group = group

        func.filters = filters
        if sudoers_only:
            func.filters = filters & filter_sudoers

        return func

    return decorator
