import contextlib
import os
import platform
from datetime import datetime

import pyrogram
from langs import Langs
from pyrogram.errors import BadRequest
from pyrogram.helpers import ikb
from rich import box, print
from rich.panel import Panel
from tortoise.exceptions import OperationalError

from userlixo.config import bot, plugins, sudoers, user
from userlixo.database import Config
from userlixo.utils import shell_exec, timezone_shortener, tryint


async def compose_startup_message(lang: Langs):
    local_version = int((await shell_exec("git rev-list --count HEAD"))[0])
    python_version = platform.python_version()
    pyrogram_version = pyrogram.__version__
    system_uname = (await shell_exec("uname -mons"))[0]

    pid = os.getpid()
    uptime = (
        await shell_exec("ps -o pid,etime --no-headers -p " + str(pid) + " | awk '{print $2}' ")
    )[0]

    user_plugins = len(list(plugins["user"]))
    bot_plugins = len(list(plugins["bot"]))
    plugins_total = user_plugins + bot_plugins
    append_plugins = f"\n├ 👤 {user_plugins}\n└ 👾 {bot_plugins}" if plugins_total else ""

    return lang.started_alert(
        version=local_version,
        pid=pid,
        python_version=python_version,
        pyrogram_version=pyrogram_version,
        server_uname=system_uname,
        uptime=uptime,
        plugins_total=plugins_total,
        append_plugins=append_plugins,
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
        print(f"[bold yellow]Error while sending startup alert to LOGS_CHAT: {e}")


async def edit_restarting_alert(lang: Langs):
    restarting_alert = await Config.filter(key="restarting_alert")
    if len(restarting_alert) > 1:
        await Config.filter(key="restarting_alert").delete()
        restarting_alert = []

    if restarting_alert:
        restarting_alert = restarting_alert[0]

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
            print(
                f"[yellow]Failed to edit the restarting alert. Maybe the message has been deleted \
    or somehow it became inaccessible.\n>> {e}[/yellow]"
            )
        with contextlib.suppress(OperationalError):
            await (await Config.get(id=restarting_alert.id)).delete()
