from collections.abc import Callable


def on_user_handler(func: Callable) -> Callable:
    func.is_user_plugin_handler = True
    return func
