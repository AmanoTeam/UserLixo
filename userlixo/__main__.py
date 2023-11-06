# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team
# ruff: noqa: E402
from pathlib import Path

import aiocron
from kink import di
from pyrogram import idle
from rich import print
from rich.console import Console
from tortoise import run_async

from userlixo.modules import (
    AssistantController,
    UserbotController,
)
from userlixo.utils.cache import clean_cache
from userlixo.utils.plugins import load_all_installed_plugins
from userlixo.utils.services.language_selector import LanguageSelector
from userlixo.utils.startup import (
    alert_startup,
    edit_restarting_alert,
    print_cli_startup_alert,
)

language_selector = di[LanguageSelector]
langs = language_selector.get_lang()

from userlixo.config import (
    bot,
    load_env,
    sudoers,
    user,
)
from userlixo.database import connect_database

console = Console()


async def main():
    with console.status("Connecting to database..."):
        await connect_database()

    with console.status("Loading env vars..."):
        await load_env()

    aiocron.crontab("*/1 * * * *")(clean_cache)

    if not Path("user.session").exists() or not Path("bot.session").exists():
        from userlixo.login import main as login

        await login()

    with console.status("Starting clients..."):
        await user.start()
        await bot.start()

    with console.status("Saving get_me info..."):
        user.me = await user.get_me()

        bot.me = await bot.get_me()
        user.assistant = bot

    if user.me.id not in sudoers:
        sudoers.append(user.me.id)

    with console.status("Loading controllers..."):
        AssistantController.__controller__.register(bot)
        UserbotController.__controller__.register(user)

    with console.status("Loading plugins..."):
        await load_all_installed_plugins()

    with console.status("Editing restart alert..."):
        await edit_restarting_alert(langs)

    with console.status("Alerting startup..."):
        await alert_startup(langs)

    await print_cli_startup_alert()

    await idle()
    await user.stop()
    await bot.stop()


if __name__ == "__main__":
    try:
        run_async(main())
    except KeyboardInterrupt:
        print("[red]Forced stop... Bye!")
    finally:
        print("[red]UserLixo stopped... Bye!")
