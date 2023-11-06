from collections.abc import Callable
from dataclasses import dataclass

from userlixo.types.handler_callable import HandlerCallable


@dataclass
class PluginElementCollection:
    pre_load: list[Callable]
    post_load: list[Callable]

    user_handlers: list[HandlerCallable]
    bot_handlers: list[HandlerCallable]

    user_controllers: list[Callable]
    bot_controllers: list[Callable]
