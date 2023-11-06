from langs import Langs
from pyrogram.helpers import ikb

from userlixo.config import plugins
from userlixo.modules.common.plugins import compose_plugin_info_text
from userlixo.utils.plugins import get_inactive_plugins


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
        lines.append([(lang.settings, f"plugin_settings {plugin_basename} {page}")])
    lines.append([(lang.back, f"list_plugins {page}")])
    keyboard = ikb(lines)

    text = compose_plugin_info_text(lang, plugin, status_line="")

    return text, keyboard
