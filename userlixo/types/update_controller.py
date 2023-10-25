import inspect
from typing import Any

from kink import di


class UpdateController:
    def __init__(self, cls):
        self.handlers = []
        self.cls = di[cls] if cls in di else cls
        self.is_instance = inspect.isclass(type(self.cls))
        self.import_handlers()

    def import_handlers(self):
        for key in dir(self.cls):
            attribute = getattr(self.cls, key)
            if not callable(attribute):
                continue

            if hasattr(attribute, "register_handler"):
                self.handlers.append(attribute)

    def import_controller(self, controller: Any):
        if not hasattr(controller, "__controller__"):
            raise TypeError("controller must be decorated with @Controller")

        self.handlers.extend(controller.__controller__.handlers)

    def register(self, client):
        for handler in self.handlers:
            handler.register_handler(client)
