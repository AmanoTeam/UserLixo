from dataclasses import dataclass

from kink import inject
from pyrogram import Client
from pyrogram.types import CallbackQuery

from userlixo.config import plugins
from userlixo.database import PluginSetting
from userlixo.modules.abstract import CallbackQueryHandler
from userlixo.modules.assistant.common.plugins import ask_and_handle_plugin_settings
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class PluginSettingResetCallbackQueryHandler(CallbackQueryHandler):
    language_selector: LanguageSelector

    async def handle_callback_query(self, client: Client, query: CallbackQuery):
        lang = self.language_selector.get_lang()

        plugin_name = query.matches[0].group("plugin_name")
        plugins_page = int(query.matches[0].group("plugins_page"))
        settings_page = int(query.matches[0].group("settings_page"))
        options_page = int(query.matches[0].group("options_page"))
        key = query.matches[0].group("key")

        plugin_info = plugins.get(plugin_name, None)

        setting = plugin_info.settings[key]

        setting.value = setting.default
        if setting.default is not None:
            await PluginSetting.update_or_create(
                defaults={"value": setting.value}, plugin=plugin_name, key=key
            )
        else:
            await PluginSetting.filter(plugin=plugin_name, key=key).delete()

        await ask_and_handle_plugin_settings(
            client,
            query,
            lang,
            setting,
            plugin_name,
            key,
            settings_page,
            options_page,
            plugins_page,
        )
        return