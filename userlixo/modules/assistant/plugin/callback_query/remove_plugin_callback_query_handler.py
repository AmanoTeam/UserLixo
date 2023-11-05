import importlib
import json
from dataclasses import dataclass
from pathlib import Path

from kink import inject
from pyrogram.types import CallbackQuery

from userlixo.config import bot, plugins, user
from userlixo.database import Config
from userlixo.modules.abstract import CallbackQueryHandler
from userlixo.modules.assistant.common.plugins import (
    compose_list_plugins_by_type_message,
)
from userlixo.utils.plugins import get_inactive_plugins
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class RemovePluginCallbackQueryHandler(CallbackQueryHandler):
    language_selector: LanguageSelector

    async def handle_callback_query(self, client, query: CallbackQuery):
        lang = self.language_selector.get_lang()

        basename = query.matches[0]["basename"]
        plugin_type = query.matches[0]["plugin_type"]
        page = int(query.matches[0]["page"])

        if basename not in plugins[plugin_type]:
            return await query.answer(lang.plugin_not_found(name=basename))

        plugin = plugins[plugin_type][basename]

        inactive = await get_inactive_plugins(plugins)

        if not Path(plugin["filename"]).exists():
            return await query.edit(lang.plugin_not_exists_on_server)

        if plugin["notation"] in inactive:
            inactive = [x for x in inactive if x != plugin["notation"]]
            await Config.get(key="INACTIVE_PLUGINS").update(value=json.dumps(inactive))

        try:
            module = importlib.import_module(plugin["notation"])
        except Exception as e:
            Path(plugin["filename"]).unlink()
            return await query.edit(lang.plugin_could_not_load(e=e))

        functions = [*filter(callable, module.__dict__.values())]
        functions = [*filter(lambda f: hasattr(f, "handlers"), functions)]

        c = (user, bot)[plugin_type == "bot"]
        for f in functions:
            for handler in f.handlers:
                c.remove_handler(*handler)
        del plugins[plugin_type][basename]
        Path(plugin["filename"]).unlink()

        await query.answer(lang.plugin_removed(name=basename))
        query.matches = [{"page": page, "type": plugin_type}]

        text, keyboard = await compose_list_plugins_by_type_message(
            lang, plugin_type, page, show_add_plugin_button=False, append_back=True
        )
        await query.edit(text, reply_markup=keyboard)
        return None