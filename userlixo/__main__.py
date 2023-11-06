# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team
# ruff: noqa: E402
import logging
import os
from pathlib import Path

import aiocron
from kink import di
from pyrogram import idle
from rich.console import Console
from rich.logging import RichHandler
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

if os.getenv("DEBUG", None) == "true" or os.getenv("LOG_LEVEL", None) == "DEBUG":
    logging.basicConfig(level="DEBUG", handlers=[RichHandler()])
else:
    log_level = os.getenv("LOG_LEVEL", "WARNING")
    logging.basicConfig(level=log_level, handlers=[RichHandler()])

logger = logging.getLogger("userlixo")
console = Console()


async def main():
    logger.debug("Connecting to database...")
    await connect_database()
    logger.debug("Connected to database!")

    logger.debug("Loading env vars...")
    await load_env()
    logger.debug("Loaded env vars!")

    logger.debug("Loading crons...")
    aiocron.crontab("*/1 * * * *")(clean_cache)
    logger.debug("Loaded crons!")

    if not Path("user.session").exists() or not Path("bot.session").exists():
        logger.debug("No sessions found, starting login...")
        from userlixo.login import main as login

        await login()
        logger.debug("Logged in!")

    logger.debug("Starting clients...")
    await user.start()
    await bot.start()
    logger.debug("Started clients!")

    logger.debug("Saving get_me info...")
    user.me = await user.get_me()

    bot.me = await bot.get_me()
    user.assistant = bot
    logger.debug("Saved get_me info!")

    if user.me.id not in sudoers:
        logger.debug("user.me.id not found in sudoers, adding it to sudoers...")
        sudoers.append(user.me.id)

    logger.debug("Loading controllers...")
    AssistantController.__controller__.register(bot)
    UserbotController.__controller__.register(user)
    logger.debug("Loaded controllers!")

    logger.debug("Loading plugins...")
    await load_all_installed_plugins()
    logger.debug("Loaded plugins!")

    logger.debug("Editing restart alert...")
    await edit_restarting_alert(langs)
    logger.debug("Edited restart alert!")

    logger.debug("Alerting startup...")
    await alert_startup(langs)
    logger.debug("Alerted startup!")

    logger.debug("Printing cli startup alert...")
    await print_cli_startup_alert()

    logger.debug("Starting idle...")
    await idle()
    logger.debug("After idle. Stopping user and bot...")
    await user.stop()
    await bot.stop()


if __name__ == "__main__":
    try:
        logger.info("Starting UserLixo...")
        run_async(main())
    except KeyboardInterrupt:
        logger.warning("Forced stop... Bye!")
    finally:
        logger.warning("UserLixo stopped... Bye!")
