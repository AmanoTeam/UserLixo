from collections.abc import Callable


def bot_controller(func: Callable) -> Callable:
    func.is_bot_plugin_controller = True
    return func
