import os
import platform
from dataclasses import dataclass

import pyrogram
from kink import inject
from pyrogram import Client, filters
from pyrogram.types import Message

from userlixo.config import plugins
from userlixo.modules.abstract import MessageHandler
from userlixo.utils import shell_exec
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class InfoMessageHandler(MessageHandler):
    language_selector: LanguageSelector

    async def handle_message(self, client: Client, message: Message):
        lang = self.language_selector.get_lang()

        act = message.edit if await filters.me(client, message) else message.reply

        pid = os.getpid()
        uptime = (
            await shell_exec(
                "ps -o pid,etime --no-headers -p " + str(pid) + " | awk '{print $2}' "
            )
        )[0]

        uname = (await shell_exec("uname -mons"))[0]
        local_version = int((await shell_exec("git rev-list --count HEAD"))[0])
        remote_version = int(
            (
                await shell_exec(
                    "curl -s -I -k 'https://api.github.com/repos/AmanoTeam/UserLixo/commits?per_page=1'"
                    + "| grep -oE '&page=[0-9]+>; rel=\"last\"' | grep -oE '[0-9]+' "
                )
            )[0]
        )
        python_version = platform.python_version()
        pyrogram_version = pyrogram.__version__

        ul_status = (
            lang.info_upgradable_to(version=remote_version)
            if local_version < remote_version
            else lang.info_latest
        )

        user_plugins = len(list(plugins["user"]))
        bot_plugins = len(list(plugins["bot"]))
        plugins_total = user_plugins + bot_plugins
        append_plugins = f"\n├ 👤 {user_plugins}\n└ 👾 {bot_plugins}" if plugins_total else ""

        text = lang.info_text(
            pid=pid,
            uptime=uptime,
            uname=uname,
            local_version=local_version,
            ul_status=ul_status,
            python_version=python_version,
            pyrogram_version=pyrogram_version,
            plugins_total=plugins_total,
            append_plugins=append_plugins,
        )
        await act(text)