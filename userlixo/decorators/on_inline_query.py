from collections.abc import Callable

from pyrogram.filters import Filter, user

from userlixo.config import sudoers


def on_inline_query(filters: Filter = None, group: int = 0, sudoers_only: bool = True) -> Callable:
    def decorator(func: Callable) -> Callable:
        func.on = "inline_query"
        func.group = group

        func.filters = filters
        if sudoers_only:
            func.filters = filters & user(sudoers)

        return func

    return decorator
