from pyrogram import filters

from userlixo.decorators import Controller, on_callback_query


@Controller()
class PluginController:
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

    @on_callback_query(filters.regex("^confirm_add_plugin (?P<plugin_type>user|bot) (?P<filename>.+)"))
    async def confirm_add_plugin(self, _c, callback_query):
        pass

    @on_callback_query(filters.regex("^list_plugins"))
    async def list_plugins(self, _c, callback_query):
        pass

    @on_callback_query(filters.regex(r"^(?P<type>user|bot)_plugins (?P<page>\d+)"))
    async def list_plugins_by_type(self, _c, callback_query):
        pass