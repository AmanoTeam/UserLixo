import contextlib
import logging
import os
import platform
import sys
from datetime import datetime

import hydrogram
from langs import Langs
from hydrogram.errors import BadRequest
from hydrogram.helpers import ikb
from rich import box, print
from rich.panel import Panel

from userlixo.config import bot, plugins, sudoers, user
from userlixo.database import Config
from userlixo.utils import shell_exec, timezone_shortener, tryint

logger = logging.getLogger(__name__)


def update_requirements():
    gray_color = "\033[1;30m"
    reset_color = "\033[0m"

    if os.getenv("IS_DOCKER"):
        os.system(
            f"{gray_color}; {sys.executable} -m pip install -r requirements.txt; {reset_color}"
        )
    else:
        os.system(f"{gray_color}; rye sync; {reset_color}")


async def compose_startup_message(lang: Langs):
    local_version = int((await shell_exec("git rev-list --count HEAD"))[0])
    python_version = platform.python_version()
    hydrogram_version = hydrogram.__version__
    system_uname = (await shell_exec("uname -mons"))[0]

    pid = os.getpid()
    uptime = (
        await shell_exec("ps -o pid,etime --no-headers -p " + str(pid) + " | awk '{print $2}' ")
    )[0]

    plugins_total = len(plugins)

    return lang.started_alert(
        version=local_version,
        pid=pid,
        python_version=python_version,
        hydrogram_version=hydrogram_version,
        server_uname=system_uname,
        uptime=uptime,
        plugins_total=plugins_total,
    )


async def compose_restarting_message(lang: Langs, cmd_timestamp: float, from_cmd: str):
    now_timestamp = datetime.now().timestamp()
    diff = round(now_timestamp - cmd_timestamp, 2)

    title, p = await shell_exec('git log --format="%B" -1')
    rev, p = await shell_exec("git rev-parse --short HEAD")
    date, p = await shell_exec('git log -1 --format=%cd --date=format:"%d/%m %H:%M"')
    timezone, p = await shell_exec('git log -1 --format=%cd --date=format:"%z"')
    local_version = int((await shell_exec("git rev-list --count HEAD"))[0])

    timezone = timezone_shortener(timezone)
    date += f" ({timezone})"

    text = lang.upgraded_alert if from_cmd.startswith("upgrade") else lang.restarted_alert

    return text(rev=rev, date=date, seconds=diff, local_version=local_version)


async def print_cli_startup_alert():
    date, p = await shell_exec('git log -1 --format=%cd --date=format:"%d/%m %H:%M"')
    timezone, p = await shell_exec('git log -1 --format=%cd --date=format:"%z"')
    local_version = int((await shell_exec("git rev-list --count HEAD"))[0])

    timezone = timezone_shortener(timezone)
    date += f" ({timezone})"
    mention = "@" + user.me.username if user.me.username else user.me.id
    text = []

    userlixo_info = {
        "Version": local_version,
        "Account": mention,
        "Bot": "@" + bot.me.username,
        "Prefixes": os.getenv("PREFIXES"),
        "Logs_chat": os.getenv("LOGS_CHAT"),
        "Sudoers": ", ".join([*set(map(str, sudoers))]),  # using set() to make the values unique
        "Commit_date": date,
    }
    for k, v in userlixo_info.items():
        text.append(f"[orchid]{k}:[/] {v}")

    text = "\n".join(text)

    print(
        Panel.fit(
            text,
            border_style="medium_purple1",
            box=box.HEAVY,
            title=":ok: [bold medium_purple1]UserLixo is running[/bold medium_purple1] :ok:",
        )
    )


async def alert_startup(lang: Langs):
    text = await compose_startup_message(lang)
    logs_chat = os.getenv("LOGS_CHAT")

    try:
        if logs_chat and logs_chat != "me":
            return await user.send_message(logs_chat, text)

        try:
            await bot.send_message(user.me.username, text)
        except BadRequest:
            await user.send_message(logs_chat, text)
    except Exception as e:
        logger.error(f"[bold yellow]Error while sending startup alert to LOGS_CHAT: {e}")


async def edit_restarting_alert(lang: Langs):
    restarting_alert = Config.get_or_none(Config.key == "restarting_alert")

    if restarting_alert:
        message_id, chat_id, cmd_timestamp, from_cmd = restarting_alert.value.split("|")

        text = await compose_restarting_message(lang, float(cmd_timestamp), from_cmd)

        kwargs = {}
        try:
            editor = bot if from_cmd.endswith("bot") else user
            if editor == bot:
                keyboard = ikb([[(lang.back, "start")]])
                kwargs.update(reply_markup=keyboard)

            if chat_id == "inline":
                await bot.edit_inline_text(message_id, text, **kwargs)
            else:
                await editor.edit_message_text(tryint(chat_id), tryint(message_id), text, **kwargs)
        except BaseException as e:
            logger.error(
                f"[yellow]Failed to edit the restarting alert. Maybe the message has been deleted \
    or somehow it became inaccessible.\n>> {e}[/yellow]"
            )

        restarting_alert.delete_instance()
