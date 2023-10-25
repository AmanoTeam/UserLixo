from pyrogram import filters

from userlixo.decorators import Controller, on_callback_query


@Controller()
class PluginController:
    @staticmethod
    @on_callback_query(
        filters.regex(
            r"^info_plugin (?P<basename>.+) (?P<plugin_type>user|bot) (?P<pg>\d+)"
        )
    )
    async def info_plugin(_c, callback_query):
        pass

    @staticmethod
    @on_callback_query(
        filters.regex(
            r"^(?P<deactivate>de)?activate_plugin (?P<basename>.+) (?P<plugin_type>user|bot) (?P<pg>\d+)"
        )
    )
    async def activate_plugin(_c, callback_query):
        pass

    @staticmethod
    @on_callback_query(
        filters.regex(
            r"^remove_plugin (?P<basename>.+) (?P<plugin_type>user|bot) (?P<page>\d+)"
        )
    )
    async def remove_plugin(_c, callback_query):
        pass

    @staticmethod
    @on_callback_query(filters.regex("^add_plugin"))
    async def add_plugin(_c, callback_query):
        pass

    @staticmethod
    @on_callback_query(filters.regex("^cancel_plugin"))
    async def cancel_plugin(_c, callback_query):
        pass

    @staticmethod
    @on_callback_query(filters.regex("^confirm_add_plugin (?P<plugin_type>user|bot) (?P<filename>.+)"))
    async def confirm_add_plugin(_c, callback_query):
        pass

    @staticmethod
    @on_callback_query(filters.regex("^list_plugins"))
    async def list_plugins(_c, callback_query):
        pass

    @staticmethod
    @on_callback_query(filters.regex(r"^(?P<type>user|bot)_plugins (?P<page>\d+)"))
    async def list_plugins_by_type(_c, callback_query):
        pass
