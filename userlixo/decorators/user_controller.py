from collections.abc import Callable

from userlixo.decorators.controller import controller


def user_controller(*args, **kwargs):
    def decorator(cls: Callable, imports: list | None = None, plugin_handler: str | None = None):
        cls = controller(imports, plugin_handler)(cls)
        cls.is_user_plugin_controller = True
        return cls

    called_without_args = len(args) == 1 and callable(args[0]) and len(kwargs) == 0

    if called_without_args:
        return decorator(args[0])

    return lambda cls: decorator(cls, *args, **kwargs)
