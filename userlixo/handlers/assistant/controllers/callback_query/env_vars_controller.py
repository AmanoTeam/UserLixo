from dataclasses import dataclass

from pyrogram import filters

from userlixo.handlers.assistant.handlers.callback_query.edit_env_callback_query_handler import (
    EditEnvCallbackQueryHandler,
)
from userlixo.handlers.assistant.handlers.callback_query.restart_now_callback_query_handler import (
    RestartNowCallbackQueryHandler,
)
from userlixo.handlers.assistant.handlers.callback_query.setting_env_callback_query_handler import (
    SettingEnvCallbackQueryHandler,
)
from userlixo.handlers.assistant.handlers.callback_query.view_env_callback_query_handler import (
    ViewEnvCallbackQueryHandler,
)
from userlixo.decorators import Controller, on_callback_query


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
