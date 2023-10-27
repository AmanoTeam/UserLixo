import importlib
import json
from dataclasses import dataclass
from pathlib import Path

from kink import inject
from pyrogram.types import CallbackQuery

from userlixo.config import bot, plugins, user
from userlixo.database import Config
from userlixo.handlers.abstract import CallbackQueryHandler
from userlixo.handlers.assistant.handlers.common.plugins import (
    compose_info_plugin_message,
)
from userlixo.utils.plugins import get_inactive_plugins
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class TogglePluginCallbackQueryHandler(CallbackQueryHandler):
    language_selector: LanguageSelector

    async def handle_callback_query(self, client, query: CallbackQuery):
        lang = self.language_selector.get_lang()

        plugin_basename = query.matches[0]["basename"]
        plugin_type = query.matches[0]["plugin_type"]
        deactivate = query.matches[0]["deactivate"]
        page = int(query.matches[0]["page"])

        if plugin_basename not in plugins[plugin_type]:
            return await query.answer(lang.plugin_not_found(name=plugin_basename))

        plugin = plugins[plugin_type][plugin_basename]
        if not Path(plugin["filename"]).exists():
            return await query.message.edit(lang.plugin_not_exists_on_server)

        inactive = await get_inactive_plugins(plugins)

        if deactivate:
            inactive.append(plugin["notation"])
        else:
            inactive = [x for x in inactive if x != plugin["notation"]]

        inactive = [*set(inactive)]  # make values unique
        await Config.get(key="INACTIVE_PLUGINS").update(value=json.dumps(inactive))

        try:
            module = importlib.import_module(plugin["notation"])
        except Exception as e:
            Path(plugin["filename"]).unlink()
            return await query.message.edit(lang.plugin_could_not_load(e=e))

        functions = [*filter(callable, module.__dict__.values())]
        functions = [*filter(lambda f: hasattr(f, "handler"), functions)]

        c = (user, bot)[plugin_type == "bot"]
        for f in functions:
            (c.remove_handler if deactivate else c.add_handler)(*f.handler)

        text = lang.plugin_has_been_deactivated if deactivate else lang.plugin_has_been_activated
        await query.answer(text)

        text, keyboard = await compose_info_plugin_message(
            lang, plugin_type, plugin_basename, page
        )

        await query.message.edit(text, reply_markup=keyboard)
        return None
