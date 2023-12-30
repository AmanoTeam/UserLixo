import datetime
import os
import platform
import time
from dataclasses import dataclass

import psutil
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
        p = psutil.Process(pid)
        start_time = p.create_time()
        now_time = time.time()
        uptime = datetime.timedelta(seconds=int(now_time - start_time))

        uname = (await shell_exec("uname -mons"))[0]
        local_version = int((await shell_exec("git rev-list --count HEAD"))[0])
        try:
            remote_version = int(
                (
                    await shell_exec(
                        "curl -s -I -k 'https://api.github.com/repos/AmanoTeam/UserLixo/commits?per_page=1'"
                        + "| grep -oE '&page=[0-9]+>; rel=\"last\"' | grep -oE '[0-9]+' "
                    )
                )[0]
            )
        except ValueError:
            remote_version = "???"

        python_version = platform.python_version()
        pyrogram_version = pyrogram.__version__

        ul_status = (
            lang.info_upgradable_to(version=remote_version)
            if local_version < remote_version
            else lang.info_latest
        ) if remote_version is int else lang.unknown

        plugins_total = len(plugins)

        text = lang.info_text(
            pid=pid,
            uptime=uptime,
            uname=uname,
            local_version=local_version,
            ul_status=ul_status,
            python_version=python_version,
            pyrogram_version=pyrogram_version,
            plugins_total=plugins_total,
        )
        await act(text)
