import inspect
from typing import Any

from kink import di
from pyrogram import Client


class UpdateController:
    def __init__(self, cls):
        self.registers = []
        self.cls = cls
        self.cls_instance = self.get_cls_instance()

        self.import_handlers()

    def get_cls_instance(self):
        return di[self.cls] if self.cls in di else self.cls()

    def get_method(self, key):
        return self.cls.__dict__[key] if key in self.cls.__dict__ else getattr(self.cls, key)

    def is_method_static(self, key):
        method = self.get_method(key)
        return isinstance(method, staticmethod)

    def get_method_callable(self, key):
        is_static = self.is_method_static(key)
        method = self.get_method(key)
        if is_static:
            return method
        else:
            is_async = inspect.iscoroutinefunction(method)

            def call(*args, **kwargs):
                return method(self.cls_instance, *args, **kwargs)

            async def async_call(*args, **kwargs):
                return await method(self.cls_instance, *args, **kwargs)

            return async_call if is_async else call

    def register_handler(self, client: Client, key, method):
        method_callable = self.get_method_callable(key)
        filters = method.filters if hasattr(method, "filters") else None
        group = method.group if hasattr(method, "group") else 0

        if method.on == "message":
            client.on_message(filters, group)(method_callable)
        elif method.on == "callback_query":
            client.on_callback_query(filters, group)(method_callable)
        elif method.on == "inline_query":
            client.on_inline_query(filters, group)(method_callable)

    def import_handlers(self):
        for key in dir(self.cls):
            method = self.get_method(key)
            if not callable(method):
                continue

            if hasattr(method, "on"):
                self.registers.append(lambda client, k=key, m=method: self.register_handler(client, k, m))

    def import_controller(self, controller: Any):
        if not hasattr(controller, "__controller__"):
            raise TypeError("controller must be decorated with @Controller")

        self.registers.extend(controller.__controller__.registers)

    def register(self, client):
        for register in self.registers:
            register(client)
