import logging

from langs import Langs
from pyrogram import filters
from pyrogram.helpers import ikb
from pyrogram.nav import Pagination
from pyrogram.types import CallbackQuery

from userlixo.config import plugins
from userlixo.database import PluginSetting
from userlixo.modules.common.plugins import compose_plugin_info_text
from userlixo.types.client import Client
from userlixo.types.plugin_settings import PluginSettings
from userlixo.types.settings_type import SettingsType
from userlixo.utils.plugins import get_inactive_plugins

logger = logging.getLogger(__name__)


async def compose_info_plugin_message(lang: Langs, plugin_basename: str, page: int):
    plugin = plugins[plugin_basename]

    inactive = await get_inactive_plugins(plugins)

    # status = lang.active
    first_btn = (
        lang.deactivate,
        f"deactivate_plugin {plugin_basename} {page}",
    )

    if plugin.name in inactive:
        # status = lang.inactive
        first_btn = (
            lang.activate,
            f"activate_plugin {plugin_basename} {page}",
        )

    lines = [
        [
            first_btn,
            (lang.remove, f"remove_plugin {plugin_basename} {page}"),
        ]
    ]
    if plugin.settings:
        lines.append([(lang.settings, f"plugin_settings {plugin_basename} 0 {page}")])
    lines.append([(lang.back, f"list_plugins {page}")])
    keyboard = ikb(lines)

    text = compose_plugin_info_text(lang, plugin, status_line="")

    return text, keyboard


def compose_plugin_settings_open_message(
    lang: Langs,
    setting: PluginSettings,
    plugin_name: str,
    key: str,
    settings_page: int,
    options_page: int,
    plugins_page: int,
):
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
        (
            (
                f"🏷 Value: {setting.value}"
                if setting.value is not None
                else "🏷 Value: &lt;empty&gt;"
            )
            if setting.type != SettingsType.bool
            else (
                f"🏷 Value: {setting.value} 🟢" if setting.value else f"🏷 Value: {setting.value} 🔴"
            )
        ),
        f"🔧 Min length: {setting.min_length}" if setting.min_length else None,
        f"🔧 Max length: {setting.max_length}" if setting.max_length else None,
        f"🔧 Pattern: {setting.pattern}" if setting.pattern else None,
        f"🔧 Min value: {setting.min_value}" if setting.min_value else None,
        f"🔧 Max value: {setting.max_value}" if setting.max_value else None,
    ]
    text_lines = [line for line in text_lines if line is not None]

    lines = []

    if setting.type == SettingsType.select:

        def compose_page_data(pg: int):
            return f"plugin_setting_open {plugin_name}" f"{key} {pg} {options_page} {plugins_page}"

        def compose_item_data(option: str | int | bool, _pg: int):
            return (
                f"PS_select {plugin_name} {key} {option}"
                f" {settings_page} {options_page} {plugins_page}"
            )

        def compose_item_title(option: str | int | bool, _pg: int):
            return f"✨ {option}" if option == setting.value else option

        nav = Pagination(setting.options, compose_page_data, compose_item_data, compose_item_title)
        lines.extend(nav.create(options_page, lines=3, columns=2))
    elif setting.type == SettingsType.bool:
        lines.append(
            [
                (
                    lang.plugin_setting_toggle_enabled
                    if setting.value
                    else lang.plugin_setting_toggle_disabled,
                    f"PS_toggle {plugin_name} {key} {settings_page} {options_page} {plugins_page}",
                )
            ]
        )
    elif setting.type in [SettingsType.text, SettingsType.range, SettingsType.int]:
        text_lines.extend(["", lang.plugin_setting_open_text_input])

    text = "\n".join(text_lines)

    lines.append([(lang.back, f"plugin_settings {plugin_name} {settings_page} {plugins_page}")])

    keyboard = ikb(lines)

    return text, keyboard


async def ask_and_handle_plugin_settings(
    client: Client,
    query: CallbackQuery,
    lang: Langs,
    setting: PluginSettings,
    plugin_name: str,
    key: str,
    settings_page: int,
    options_page: int,
    plugins_page: int,
):
    text, keyboard = compose_plugin_settings_open_message(
        lang, setting, plugin_name, key, settings_page, options_page, plugins_page
    )

    await query.edit(text, reply_markup=keyboard)
    last_msg = query.message

    try:
        while True:
            user_id = query.from_user.id
            msg = await client.listen(chat_id=user_id, user_id=user_id, filters=filters.text)
            await last_msg.remove_keyboard()

            plugin_info = plugins.get(plugin_name, None)
            if not plugin_info:
                return await msg.reply_text(lang.plugin_not_found(name=plugin_name))

            if not plugin_info.settings:
                return await msg.reply_text(
                    lang.plugin_settings_not_found(plugin_name=plugin_name)
                )

            if key not in plugin_info.settings:
                return await msg.reply_text(
                    lang.plugin_setting_not_found(plugin_name=plugin_name, key=key)
                )

            plugin_setting = plugin_info.settings[key]

            plugin_setting.value = msg.text
            await PluginSetting.update_or_create(
                defaults={"value": msg.text}, plugin=plugin_name, key=key
            )

            text, keyboard = compose_plugin_settings_open_message(
                lang, setting, plugin_name, key, settings_page, options_page, plugins_page
            )

            last_msg = await msg.reply_text(text, reply_markup=keyboard)
    except Exception as e:
        logger.exception(e)
