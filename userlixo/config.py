# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

import configparser
import json
import logging
import os
import re

import pyrogram
from pyrogram import filters
from pyrogram.helpers import bki
from pyrogram.utils import PyromodConfig

from userlixo.database import Config
from userlixo.types.client import Client
from userlixo.types.plugin_info import PluginInfo
from userlixo.utils.misc import b64decode, b64encode, tryint
from userlixo.utils.patches import edit_text, query_edit, remove_keyboard, reply_text

from rich import print

sudoers = []

logger = logging.getLogger(__name__)


async def load_env():
    environment_vars: dict = {
        "DATABASE_URL": [
            "sqlite://userlixo/database/database.sqlite",
            "Address of the database (sqlite or postgres).",
        ],
        "LANGUAGE": ["en", "Language for UserLixo's strings"],
        "LOGS_CHAT": [
            "me",
            "Chat where the logs (e.g. startup alert) will be sent. Can be username, link or id.",
        ],
        "PREFIXES": [".", "Prefixes for the userbot commands"],
        "SUDOERS_LIST": [
            "",
            "List of users (usernames and ids separated by space) that will have permission to \
use your userbot/assistant.",
        ],
        "BOT_TOKEN": ["", "Token of the assistant inline bot"],
        "WEB_APP_URL": ["https://webapp.pauxis.dev/userlixo/", "URL of the webapp."],
    }

    restricted_vars = ["DATABASE_URL"]
    required_vars = ["BOT_TOKEN", "WEB_APP_URL"]
    missing_vars = []
    for env_key, (default_value, env_info) in environment_vars.items():
        value_on_env = os.getenv(env_key, default_value)

        value_on_db = Config.get_or_none(Config.key == env_key)

        if not value_on_db:
            if env_key in restricted_vars:
                os.environ[env_key] = value_on_env
            else:
                missing_vars.append([env_key, value_on_env, env_info])
            continue
        os.environ[env_key] = value_on_db.value

    if missing_vars:
        if len(missing_vars) == len(environment_vars.keys()) - len(restricted_vars):
            text = "[dodger_blue1 bold underline]Welcome to UserLixo![/][deep_sky_blue1]\nAs the \
first step we need to setup some config vars.\n\nYou will be asked for a value for each var, but \
you can just press enter to leave it empty or use the default value. Let's get started![/]"
        else:
            text = "[bold yellow]Some required config vars are missing. Let's add them.[/]"
        logger.info(text)
    for env_key, value_on_env, env_info in missing_vars:
        text = f"\n┌ [light_sea_green]{env_key}[/light_sea_green]"
        if value_on_env != "":
            text += f" [deep_sky_blue4](default: {value_on_env})[/]"
        elif env_key in required_vars:
            text += " [yellow](required)[/]"
        text += f"\n├ [medium_purple4 italic]{env_info}[/]"
        print(text)

        try:
            user_value = input("└> ")
        except (KeyboardInterrupt, EOFError):
            logger.info("[red1]Operation cancelled by user")
            exit()
        if not user_value:
            user_value = value_on_env

        if env_key in required_vars and not user_value:
            logger.info(f"[red1]{env_key} is required, cannot be empty.")
            exit()

        row = Config.create(key=env_key, value=user_value)
        os.environ[env_key] = row.value

    # Sanitize sudoers list
    parts = os.getenv("SUDOERS_LIST").split()
    parts = [*(tryint(x.lstrip("@").lower()) for x in parts)]
    parts = [*set(parts)]
    parts = [x for x in parts if x != "me"]
    sudoers.extend(parts)


# Extra **kwargs for creating pyrogram.Client (contains api_hash and api_id)
pyrogram_config = os.getenv("PYROGRAM_CONFIG") or b64encode("{}")
pyrogram_config = b64decode(pyrogram_config)
pyrogram_config = json.loads(pyrogram_config)

# parse config.ini values
config = configparser.ConfigParser()
api_id = config.get("pyrogram", "api_id", fallback=None)
api_hash = config.get("pyrogram", "api_hash", fallback=None)
bot_token = config.get("pyrogram", "bot_token", fallback=None)


# All monkeypatch stuff must be done before the Client instance is created
def filter_sudoers_logic(flt, c, u):
    if not u.from_user:
        return None
    user = u.from_user
    return user.id in sudoers or (user.username and user.username.lower() in sudoers)


def filter_su_cmd(command, prefixes=None, *args, **kwargs):
    async def callback(flt, c, u):
        _prefixes = prefixes or os.getenv("PREFIXES") or "."
        prefix = ""
        if " " in _prefixes:
            _prefixes = "|".join(re.escape(prefix) for prefix in _prefixes.split())
            prefix = f"({_prefixes})"
        elif isinstance(_prefixes, list | str):
            if isinstance(_prefixes, list):
                _prefixes = "".join(_prefixes)
            prefix = f"[{re.escape(_prefixes)}]"

        in_sudoers = filters.sudoers(c, u)
        matches = await filters.regex(r"^" + prefix + command, *args, **kwargs)(c, u)

        return in_sudoers and matches

    return filters.create(callback, "FilterSuCmd")


def filter_web_app_data(flt, c, u):
    return u.web_app_data


def filter_web_data_command(command, *args, **kwargs):
    async def func(flt, c, u):
        return u.web_app_data and u.web_app_data.data.startswith(command)

    return filters.create(func, "FilterWebDataCommand")


def message_ikb(self):
    return bki(self.reply_markup)


filter_sudoers = filters.create(filter_sudoers_logic, "FilterSudoers")
pyrogram.filters.sudoers = filter_sudoers
pyrogram.filters.su_cmd = filter_su_cmd
pyrogram.filters.web_app_data = filters.create(filter_web_app_data, "FilterWebAppData")
pyrogram.filters.web_data_cmd = filter_web_data_command
pyrogram.types.CallbackQuery.edit = query_edit
pyrogram.types.Message.remove_keyboard = remove_keyboard
pyrogram.types.Message.reply = reply_text
pyrogram.types.Message.edit = edit_text
pyrogram.types.Message.ikb = message_ikb

# I don't use os.getenv('KEY', fallback) because the fallback wil only be used if the key doesn't
# exist. I want to use the fallback also when the key exists but it's invalid
user = Client(
    os.getenv("PYROGRAM_SESSION") or "user",
    plugins={"enabled": False},
    workdir=".",
    api_id=api_id,
    api_hash=api_hash,
    **pyrogram_config,
)

bot = Client(
    "bot",
    plugins={"enabled": False},
    api_id=api_id,
    api_hash=api_hash,
    bot_token=os.getenv("BOT_TOKEN"),
    workdir=".",
    **pyrogram_config,
)

PyromodConfig.unallowed_click_alert = False

cmds_list = [
    "help",
    "ping",
    "upgrade",
    "restart",
    "eval",
    "exec",
    "cmd",
    "settings",
    "plugins",
    "commands",
    "start",
]
cmds = {x: 1 for x in cmds_list}

plugins: dict[str, PluginInfo] = {}
