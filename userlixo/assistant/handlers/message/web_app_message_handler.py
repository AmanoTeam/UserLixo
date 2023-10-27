import json
import os
import urllib
from dataclasses import dataclass

import psutil
from kink import inject
from pyrogram.helpers import kb
from pyrogram.types import Message, WebAppInfo

from userlixo.assistant.handlers.abstract import MessageHandler
from userlixo.config import user, cmds, plugins
from userlixo.services.language_selector import LanguageSelector
from userlixo.utils import shell_exec


@inject
@dataclass
class WebAppMessageHandler(MessageHandler):
    language_selector: LanguageSelector

    async def handle_message(self, _c, m: Message):
        local_version = int((await shell_exec("git rev-list --count HEAD"))[0])
        p = psutil.Process(os.getpid())
        start_time = p.create_time()

        info = await user.get_me()

        info_json = json.dumps(
            {
                "version": local_version,
                "start_time": start_time,
                "name": info.full_name,
                "id": info.id,
                "picture": f"https://t.me/i/userpic/160/{info.username}.jpg",
            }
        )
        settings_json = json.dumps(
            {
                "language": os.getenv("LANGUAGE"),
                "sudoers": os.getenv("SUDOERS_LIST"),
                "logs_chat": os.getenv("LOGS_CHAT"),
                "prefixes": os.getenv("PREFIXES"),
                "web_app_url": os.getenv("WEB_APP_URL"),
            }
        )

        cmds_json = json.dumps([k for k, v in cmds.items()])
        plugins_json = json.dumps(plugins)

        params = {
            "settings": settings_json,
            "info": info_json,
            "commands": cmds_json,
            "plugins": plugins_json,
        }
        query = urllib.parse.urlencode(params)

        web_app_url = os.getenv("WEB_APP_URL")
        web_app_info = WebAppInfo(url=f"{web_app_url}?{query}")

        keyboard = kb(
            [
                [
                    {
                        "text": "Settings",
                        "web_app": web_app_info,
                    }
                ]
            ]
        )
        await m.reply("Here is your webapp for settings...", reply_markup=keyboard)
