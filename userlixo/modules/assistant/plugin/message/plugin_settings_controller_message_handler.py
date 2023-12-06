from dataclasses import dataclass

from kink import inject
from hydrogram import Client
from hydrogram.types import Message

from userlixo.config import plugins
from userlixo.modules.abstract import MessageHandler
from userlixo.modules.assistant.common.plugins import compose_plugin_settings_message
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class PluginSettingsMessageHandler(MessageHandler):
    language_selector: LanguageSelector

    async def handle_message(self, client: Client, message: Message):
        lang = self.language_selector.get_lang()

        plugin_name = message.matches[0].group("plugin_name")
        plugins_page = int(message.matches[0].group("plugins_page"))
        settings_page = int(message.matches[0].group("settings_page"))

        plugin_info = plugins.get(plugin_name, None)
        if not plugin_info:
            return await message.reply(lang.plugin_not_found(name=plugin_name))

        if not plugin_info.settings:
            return await message.reply(
                lang.plugin_settings_not_found(plugin_name=plugin_name)
            )

        await client.stop_listening(chat_id=message.chat.id)

        text, keyboard = compose_plugin_settings_message(
            lang, plugin_name, plugins_page, settings_page
        )
        await message.reply(text, reply_markup=keyboard, quote=True)
        return None
