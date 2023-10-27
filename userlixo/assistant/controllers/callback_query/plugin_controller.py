from dataclasses import dataclass

from pyrogram import filters
from pyrogram.types import CallbackQuery

from userlixo.assistant.handlers.callback_query.list_plugins_callback_query_handler import (
    ListPluginsCallbackQueryHandler,
)
from userlixo.decorators import Controller, on_callback_query


@Controller()
@dataclass
class PluginController:
    list_plugins_handler: ListPluginsCallbackQueryHandler

    @on_callback_query(
        filters.regex(
            r"^info_plugin (?P<basename>.+) (?P<plugin_type>user|bot) (?P<pg>\d+)"
        )
    )
    async def info_plugin(self, _c, callback_query):
        pass

    @on_callback_query(
        filters.regex(
            r"^(?P<deactivate>de)?activate_plugin (?P<basename>.+) (?P<plugin_type>user|bot) (?P<pg>\d+)"
        )
    )
    async def activate_plugin(self, _c, callback_query):
        pass

    @on_callback_query(
        filters.regex(
            r"^remove_plugin (?P<basename>.+) (?P<plugin_type>user|bot) (?P<page>\d+)"
        )
    )
    async def remove_plugin(self, _c, callback_query):
        pass

    @on_callback_query(filters.regex("^add_plugin"))
    async def add_plugin(self, _c, callback_query):
        pass

    @on_callback_query(filters.regex("^cancel_plugin"))
    async def cancel_plugin(self, _c, callback_query):
        pass

    @on_callback_query(
        filters.regex("^confirm_add_plugin (?P<plugin_type>user|bot) (?P<filename>.+)")
    )
    async def confirm_add_plugin(self, _c, callback_query):
        pass

    @on_callback_query(filters.regex("^list_plugins"))
    async def list_plugins(self, _c, callback_query: CallbackQuery):
        await self.list_plugins_handler.handle_callback_query(_c, callback_query)

    @on_callback_query(filters.regex(r"^(?P<type>user|bot)_plugins (?P<page>\d+)"))
    async def list_plugins_by_type(self, _c, callback_query):
        pass
