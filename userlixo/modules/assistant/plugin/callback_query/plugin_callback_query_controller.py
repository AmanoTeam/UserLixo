from dataclasses import dataclass

from pyrogram import filters

from userlixo.decorators import controller, on_callback_query

from .add_plugin_callback_query_handler import AddPluginCallbackQueryHandler
from .cancel_plugin_callback_query_handler import CancelPluginCallbackQueryHandler
from .confirm_add_plugin_callback_query_handler import ConfirmAddPluginCallbackQueryHandler
from .info_plugin_callback_query_handler import InfoPluginCallbackQueryHandler
from .list_plugins_callback_query_handler import ListPluginsCallbackQueryHandler
from .plugin_setting_open_callback_query_handler import PluginSettingOpenCallbackQueryHandler
from .plugin_setting_select_callback_query_handler import PluginSettingSelectCallbackQueryHandler
from .plugin_settings_callback_query_handler import PluginSettingsCallbackQueryHandler
from .remove_plugin_callback_query_handler import RemovePluginCallbackQueryHandler
from .toggle_plugin_callback_query_handler import TogglePluginCallbackQueryHandler


@controller
@dataclass
class PluginCallbackQueryController:
    list_plugins_handler: ListPluginsCallbackQueryHandler
    toggle_plugin_handler: TogglePluginCallbackQueryHandler
    info_plugin_handler: InfoPluginCallbackQueryHandler
    remove_plugin_handler: RemovePluginCallbackQueryHandler
    plugin_settings_handler: PluginSettingsCallbackQueryHandler
    plugin_setting_open_handler: PluginSettingOpenCallbackQueryHandler
    plugin_setting_select_handler: PluginSettingSelectCallbackQueryHandler
    add_plugin_handler: AddPluginCallbackQueryHandler
    cancel_plugin_handler: CancelPluginCallbackQueryHandler
    confirm_add_plugin_handler: ConfirmAddPluginCallbackQueryHandler

    @on_callback_query(filters.regex(r"^info_plugin (?P<basename>.+) (?P<page>\d+)"))
    async def info_plugin(self, _c, callback_query):
        await self.info_plugin_handler.handle_callback_query(_c, callback_query)

    @on_callback_query(
        filters.regex(r"^(?P<deactivate>de)?activate_plugin (?P<basename>.+)" + r" (?P<page>\d+)")
    )
    async def toggle_plugin(self, _c, callback_query):
        await self.toggle_plugin_handler.handle_callback_query(_c, callback_query)

    @on_callback_query(filters.regex(r"^remove_plugin (?P<basename>.+) (?P<page>\d+)"))
    async def remove_plugin(self, _c, callback_query):
        await self.remove_plugin_handler.handle_callback_query(_c, callback_query)

    @on_callback_query(
        filters.regex(
            r"^plugin_settings (?P<plugin_name>.+) (?P<settings_page>\d+) (?P<plugins_page>\d+)"
        )
    )
    async def plugin_settings(self, _c, callback_query):
        await self.plugin_settings_handler.handle_callback_query(_c, callback_query)

    @on_callback_query(
        filters.regex(
            r"^plugin_setting_open (?P<plugin_name>.+) (?P<key>.+) "
            r"(?P<settings_page>\d+) (?P<options_page>\d+) (?P<plugins_page>\d+)"
        )
    )
    async def plugin_setting_open(self, _c, callback_query):
        await self.plugin_setting_open_handler.handle_callback_query(_c, callback_query)

    @on_callback_query(
        filters.regex(
            r"^PS_select (?P<plugin_name>.+) (?P<key>.+) (?P<option>.+)"
            r" (?P<settings_page>\d+) (?P<options_page>\d+) (?P<plugins_page>\d+)"
        )
    )
    async def plugin_setting_select(self, _c, callback_query):
        await self.plugin_setting_select_handler.handle_callback_query(_c, callback_query)

    @on_callback_query(filters.regex("^add_plugin"))
    async def add_plugin(self, _c, callback_query):
        await self.add_plugin_handler.handle_callback_query(_c, callback_query)

    @on_callback_query(filters.regex("^cancel_plugin"))
    async def cancel_plugin(self, _c, callback_query):
        await self.cancel_plugin_handler.handle_callback_query(_c, callback_query)

    @on_callback_query(filters.regex("^confirm_add_plugin (?P<filename>.+)"))
    async def confirm_add_plugin(self, _c, callback_query):
        await self.confirm_add_plugin_handler.handle_callback_query(_c, callback_query)

    @on_callback_query(filters.regex(r"^list_plugins (?P<page>\d+)"))
    async def list_plugins_by_type(self, _c, callback_query):
        await self.list_plugins_handler.handle_callback_query(_c, callback_query)
