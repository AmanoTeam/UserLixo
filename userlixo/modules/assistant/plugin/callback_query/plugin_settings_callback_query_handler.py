from dataclasses import dataclass

from kink import inject
from pyrogram import Client
from pyrogram.helpers import ikb
from pyrogram.nav import Pagination
from pyrogram.types import CallbackQuery

from userlixo.config import plugins
from userlixo.modules.abstract import CallbackQueryHandler
from userlixo.types.plugin_settings import PluginSettings
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class PluginSettingsCallbackQueryHandler(CallbackQueryHandler):
    language_selector: LanguageSelector

    async def handle_callback_query(self, _client: Client, query: CallbackQuery):
        lang = self.language_selector.get_lang()

        plugin_name = query.matches[0].group("plugin_name")
        plugins_page = int(query.matches[0].group("plugins_page"))
        settings_page = int(query.matches[0].group("settings_page"))

        plugin_info = plugins.get(plugin_name, None)
        if not plugin_info:
            return await query.answer(lang.plugin_not_found(name=plugin_name), show_alert=True)

        if not plugin_info.settings:
            return await query.answer(
                lang.plugin_settings_not_found(plugin_name=plugin_name), show_alert=True
            )

        def compose_page_data(page: int):
            return f"plugin_settings {plugin_name} {page} {plugins_page}"

        def compose_title(item: tuple[str, PluginSettings], _page: int):
            key, value = item
            return f"⚙️ {value.label}"

        def compose_data(item: tuple[str, PluginSettings], _page: int):
            key, value = item
            return f"plugin_setting_open {plugin_name} {key} {settings_page} 0 {plugins_page}"

        nav = Pagination(
            list(plugin_info.settings.items()), compose_page_data, compose_data, compose_title
        )
        lines = nav.create(settings_page, lines=3, columns=2)

        lines.append([(lang.back, f"info_plugin {plugin_name} {plugins_page}")])

        keyboard = ikb(lines)

        text = lang.plugin_settings_text(plugin_name=plugin_name)

        return await query.edit(text, reply_markup=keyboard)
