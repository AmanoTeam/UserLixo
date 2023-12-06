import json
from dataclasses import dataclass
from pathlib import Path

from kink import inject
from hydrogram.types import CallbackQuery

from userlixo.config import plugins
from userlixo.database import Config
from userlixo.modules.abstract import CallbackQueryHandler
from userlixo.modules.assistant.common.plugins import (
    compose_info_plugin_message,
)
from userlixo.utils.plugins import get_inactive_plugins, load_plugin, unload_plugin
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class TogglePluginCallbackQueryHandler(CallbackQueryHandler):
    language_selector: LanguageSelector

    async def handle_callback_query(self, client, query: CallbackQuery):
        lang = self.language_selector.get_lang()

        plugin_basename = query.matches[0]["basename"]
        deactivate = query.matches[0]["deactivate"]
        page = int(query.matches[0]["page"])

        if plugin_basename not in plugins:
            return await query.answer(lang.plugin_not_found(name=plugin_basename))

        plugin = plugins[plugin_basename]
        if not Path(plugin.folder_path).exists():
            return await query.edit(lang.plugin_not_exists_on_server)

        inactive = await get_inactive_plugins(plugins)

        if deactivate:
            inactive.append(plugin.name)
        else:
            inactive = [x for x in inactive if x != plugin.name]

        inactive = [*set(inactive)]  # make values unique
        inactive_plugins: Config = Config.get(Config.key == "INACTIVE_PLUGINS")
        inactive_plugins.update(value=json.dumps(inactive))

        if deactivate:
            await unload_plugin(plugin.name)
        else:
            await load_plugin(plugin.name)

        text = lang.plugin_has_been_deactivated if deactivate else lang.plugin_has_been_activated
        await query.answer(text)

        is_inline = query.inline_message_id is not None

        text, keyboard = await compose_info_plugin_message(
            lang, plugin_basename, page, use_deeplink=is_inline
        )

        await query.edit(text, reply_markup=keyboard, disable_web_page_preview=True)
        return None
