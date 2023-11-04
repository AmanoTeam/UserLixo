from collections.abc import Callable


def bot_handler(func: Callable) -> Callable:
    func.is_bot_plugin_handler = True
    return func
