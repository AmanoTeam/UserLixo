from typing import Callable, Any

from pyrogram import filters, Client


def on_callback_query(
    update_filters: Any = None,
    group: int = 0,
    handler: Callable = None,
    sudoers_only: bool = True,
):
    validated_filters = (
        filters.sudoers & update_filters if sudoers_only else update_filters
    )
    Client.on_callback_query(validated_filters, group)(handler)
