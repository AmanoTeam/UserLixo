from collections.abc import Callable


def user_controller(func: Callable) -> Callable:
    func.is_user_plugin_controller = True
    return func
