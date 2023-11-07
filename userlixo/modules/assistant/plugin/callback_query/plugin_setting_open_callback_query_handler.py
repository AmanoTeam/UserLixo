from dataclasses import dataclass

from kink import inject
from pyrogram import Client
from pyrogram.helpers import ikb
from pyrogram.nav import Pagination
from pyrogram.types import CallbackQuery

from userlixo.config import plugins
from userlixo.modules.abstract import CallbackQueryHandler
from userlixo.types.settings_type import SettingsType
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class PluginSettingOpenCallbackQueryHandler(CallbackQueryHandler):
    language_selector: LanguageSelector

    async def handle_callback_query(self, _client: Client, query: CallbackQuery):
        lang = self.language_selector.get_lang()

        plugin_name = query.matches[0].group("plugin_name")
        plugins_page = int(query.matches[0].group("plugins_page"))
        settings_page = int(query.matches[0].group("settings_page"))
        options_page = int(query.matches[0].group("options_page"))
        key = query.matches[0].group("key")

        plugin_info = plugins.get(plugin_name, None)
        if not plugin_info:
            return await query.answer(lang.plugin_not_found(name=plugin_name), show_alert=True)

        if not plugin_info.settings:
            return await query.answer(
                lang.plugin_settings_not_found(plugin_name=plugin_name), show_alert=True
            )

        if key not in plugin_info.settings:
            return await query.answer(
                lang.plugin_setting_not_found(plugin_name=plugin_name, key=key), show_alert=True
            )

        setting = plugin_info.settings[key]

        text_lines = [
            lang.plugin_setting_open_text(plugin_name=plugin_name, key=key),
            "",
            f"⚙️ Label: {setting.label}",
            (
                f"ℹ️ Type: {setting.type.value}. {setting.description}"
                if setting.description
                else f"ℹ️ Type: {setting.type.value}"
            ),
            "",
            f"🏷 Value: {setting.value}" if setting.value else "🏷 Value: <empty>" "",
            f"🔧 Min length: {setting.min_length}" if setting.min_length else None,
            f"🔧 Max length: {setting.max_length}" if setting.max_length else None,
            f"🔧 Pattern: {setting.pattern}" if setting.pattern else None,
            f"🔧 Min value: {setting.min_value}" if setting.min_value else None,
            f"🔧 Max value: {setting.max_value}" if setting.max_value else None,
        ]
        text_lines = [line for line in text_lines if line is not None]
        text = "\n".join(text_lines)

        lines = []

        if setting.type == SettingsType.select:

            def compose_page_data(pg: int):
                return (
                    f"plugin_setting_open {plugin_name}"
                    f"{key} {pg} {options_page} {plugins_page}"
                )

            def compose_item_data(option: str | int | bool, _pg: int):
                return f"PS_select {plugin_name} {key} {option} {plugins_page}"

            def compose_item_title(option: str | int | bool, _pg: int):
                return f"✨ {option}" if option == setting.value else option

            nav = Pagination(
                setting.options, compose_page_data, compose_item_data, compose_item_title
            )
            lines.extend(nav.create(options_page, lines=3, columns=2))

        lines.append(
            [(lang.back, f"plugin_settings {plugin_name} {settings_page} {plugins_page}")]
        )

        keyboard = ikb(lines)

        await query.edit(text, reply_markup=keyboard)
        return None
