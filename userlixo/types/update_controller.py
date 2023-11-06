import inspect
from typing import Any

from kink import di
from pyrogram import Client
from pyrogram.handlers import CallbackQueryHandler, InlineQueryHandler, MessageHandler


class UpdateController:
    def __init__(self, cls, plugin_handler: str | None = None):
        self.registers = []
        self.unregisters = []
        self.cls = cls
        self.cls_instance = self.get_cls_instance()
        self.plugin_handler = plugin_handler

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

        is_async = inspect.iscoroutinefunction(method)

        def call(*args, **kwargs):
            return method(self.cls_instance, *args, **kwargs)

        async def async_call(*args, **kwargs):
            return await method(self.cls_instance, *args, **kwargs)

        return async_call if is_async else call

    def register_handler(
        self, client: Client, plugin_handler: str | None = None, key=None, method=None
    ):
        method_callable = self.get_method_callable(key)
        filters = method.filters if hasattr(method, "filters") else None
        group = method.group if hasattr(method, "group") else 0

        handler = None
        if method.on == "message":
            handler = client.add_handler(MessageHandler(method_callable, filters), group)
        elif method.on == "callback_query":
            handler = client.add_handler(CallbackQueryHandler(method_callable, filters), group)
        elif method.on == "inline_query":
            handler = client.add_handler(InlineQueryHandler(method_callable, filters), group)

        if handler is not None:
            if plugin_handler is not None:
                h, group = handler
                h.plugin_handler = plugin_handler

            def unregister():
                client.remove_handler(*handler)

            self.unregisters.append(unregister)

    def import_handlers(self):
        for key in dir(self.cls):
            method = self.get_method(key)
            if not callable(method):
                continue

            if hasattr(method, "on"):
                self.registers.append(
                    lambda client, plugin_handler, k=key, m=method: self.register_handler(
                        client, plugin_handler, k, m
                    )
                )

    def import_controller(self, controller: Any):
        if not hasattr(controller, "__controller__"):
            raise TypeError("controller must be decorated with @Controller")

        self.registers.extend(controller.__controller__.registers)

    def register(self, client, plugin_handler: str | None = None):
        for register in self.registers:
            register(client, plugin_handler=plugin_handler)

    def unregister(self, client):
        for unregister in self.unregisters:
            unregister(client)
