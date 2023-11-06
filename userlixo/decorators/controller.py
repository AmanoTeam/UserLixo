from collections.abc import Callable

from kink import inject

from userlixo.types import UpdateController


def controller(*args, **kwargs):
    def decorator(cls: Callable, imports: list | None = None, plugin_handler: str | None = None):
        if imports is None:
            imports = []

        cls = inject(cls)
        update_controller = UpdateController(cls, plugin_handler=plugin_handler)

        for c in imports:
            update_controller.import_controller(c)

        cls.__controller__ = update_controller

        return cls

    called_without_args = len(args) == 1 and callable(args[0]) and len(kwargs) == 0

    if called_without_args:
        return decorator(args[0])

    return lambda cls: decorator(cls, *args, **kwargs)
