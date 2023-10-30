from dataclasses import dataclass

from pyrogram import filters

from userlixo.decorators import Controller, on_callback_query
from userlixo.handlers.assistant.handlers.callback_query import (
    EditEnvCallbackQueryHandler,
    RestartNowCallbackQueryHandler,
    SettingEnvCallbackQueryHandler,
    ViewEnvCallbackQueryHandler,
)


@Controller()
@dataclass
class EnvVarsController:
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
