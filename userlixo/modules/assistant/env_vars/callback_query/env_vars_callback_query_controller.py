from dataclasses import dataclass

from pyrogram import filters

from userlixo.decorators import controller, on_callback_query

from .edit_env_callback_query_handler import EditEnvCallbackQueryHandler
from .restart_now_callback_query_handler import RestartNowCallbackQueryHandler
from .setting_env_callback_query_handler import SettingEnvCallbackQueryHandler
from .view_env_callback_query_handler import ViewEnvCallbackQueryHandler


@controller
@dataclass
class EnvVarsCallbackQueryController:
    setting_env_handler: SettingEnvCallbackQueryHandler
    edit_env_handler: EditEnvCallbackQueryHandler
    view_env_handler: ViewEnvCallbackQueryHandler
    restart_now_handler: RestartNowCallbackQueryHandler

    @on_callback_query(filters.regex("^setting_env"))
    async def setting_env(self, c, callback_query):
        await self.setting_env_handler.handle_callback_query(c, callback_query)

    @on_callback_query(filters.regex("^edit_env (?P<key>.+)"))
    async def edit_env(self, c, callback_query):
        await self.edit_env_handler.handle_callback_query(c, callback_query)

    @on_callback_query(filters.regex("^view_env (?P<key>.+)"))
    async def view_env(self, c, callback_query):
        await self.view_env_handler.handle_callback_query(c, callback_query)

    @on_callback_query(filters.regex("^restart_now"))
    async def restart_now(self, c, callback_query):
        await self.restart_now_handler.handle_callback_query(c, callback_query)
