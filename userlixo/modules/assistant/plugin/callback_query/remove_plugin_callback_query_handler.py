from dataclasses import dataclass
from pathlib import Path

from kink import inject
from hydrogram.types import CallbackQuery

from userlixo.config import plugins
from userlixo.modules.abstract import CallbackQueryHandler
from userlixo.modules.common.plugins import compose_list_plugins_message
from userlixo.utils.plugins import unload_and_remove_plugin
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class RemovePluginCallbackQueryHandler(CallbackQueryHandler):
    language_selector: LanguageSelector

    async def handle_callback_query(self, client, query: CallbackQuery):
        lang = self.language_selector.get_lang()

        basename = query.matches[0]["basename"]
        page = int(query.matches[0]["page"])

        if basename not in plugins:
            return await query.answer(lang.plugin_not_found(name=basename))

        plugin = plugins[basename]

        if not Path(plugin.folder_path).exists():
            return await query.edit(lang.plugin_not_exists_on_server)

        await unload_and_remove_plugin(basename)
        del plugins[basename]

        await query.answer(lang.plugin_removed(name=basename))
        query.matches = [{"page": page}]

        is_inline = query.inline_message_id is not None

        text, keyboard = await compose_list_plugins_message(
            lang, page, append_back=True, use_deeplink=is_inline
        )
        await query.edit(text, reply_markup=keyboard)
        return None
