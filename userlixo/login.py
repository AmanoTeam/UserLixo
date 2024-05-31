# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

import asyncio
import base64
import configparser
import json
import os
import sys
from pathlib import Path

import click
import hydrogram.errors
from hydrogram import Client
from rich import print


def raise_ex(e):
    raise e


def b64encode(value: str):
    return base64.b64encode(value.encode()).decode()


def b64decode(value: str):
    return base64.b64decode(value.encode()).decode()


async def main():
    config = get_config()
    print_welcome_message()

    update_config_with_user_input(config)

    login_user = await check_existing_user_session()

    if login_user:
        create_new_user_session()
    else:
        login_using_existing_user_session()

    api_id, api_hash, bot_token = parse_config_values(config)

    user = await start_user_client(api_id, api_hash)
    session_config, session_string = await get_user_session_data(user)

    print_session_data(session_config, session_string)

    login_bot = await check_existing_bot_session(api_id, api_hash, bot_token)

    bot = await login_assistant_bot(login_bot, api_id, api_hash, bot_token)

    await user.stop()
    await bot.stop()


def get_config():
    config = configparser.ConfigParser()
    if Path("config.ini").exists():
        config.read("config.ini")
    elif Path(Path("~/.hydrogramrc").expanduser()).exists():
        config.read(Path("~/.hydrogramrc").expanduser())
    config.setdefault("hydrogram", {})
    return config


def print_welcome_message():
    text = "[bold dodger_blue1]Almost there![/]\n[deep_sky_blue1]Now we are going to login into \
the user and bot accounts."
    if __name__ == "__main__":
        text = "[bold dodger_blue1 underline]Welcome to UserLixo![/]\n[deep_sky_blue1]We are \
going to login into the user account to get PYROGRAM_CONFIG and PYROGRAM_SESSION values."
    text += "\n\nYou will be asked for a value for each var, but you can just press enter to use \
the default value (if there be any). Let's get started![/]"
    print(text)


def update_config_with_user_input(config):
    fields = ["api_id", "api_hash"]

    for key in fields:
        text = f"\n┌ [light_sea_green]{key}[/light_sea_green]"
        if key in config["hydrogram"]:
            text += f" [deep_sky_blue4](default: {config["hydrogram"][key]})[/]"
        print(text)

        try:
            user_value = input("└> ")
        except (KeyboardInterrupt, EOFError):
            print("[red1]Operation cancelled by user")
            sys.exit()
        if not user_value:
            user_value = config["hydrogram"].get(key, "")
        if not user_value:
            print(f"[red1]{key} is required, cannot be empty.")
            sys.exit()
        config["hydrogram"][key] = user_value

    with Path("config.ini").open("w", encoding="utf-8") as fp:
        config.write(fp)


async def check_existing_user_session():
    login_user = True
    if Path("user.session").exists():
        async with Client("user", workdir=".", plugins={"enabled": False}) as user:
            me = await user.get_me()
        mention = "@" + me.username if me.username else me.first_name
        print(
            rf"[bold yellow]I found an existing session from account [/][cyan]{mention}[/]"
            rf"[bold yellow]. Do you want to use it?[/] [cyan]\[yn][/]",
            end="",
        )
        c = click.getchar(True)
        login_user = c == "n"
    return login_user


def create_new_user_session():
    print("\n\n[bold green]- Logging in and creating new user.session...")

    if Path("user.session").exists():
        Path("user.session").unlink()


def login_using_existing_user_session():
    print("\n\n[bold green]- Logging in using existing user.session...")


def parse_config_values(config):
    api_id = config.get("hydrogram", "api_id", fallback=None)
    api_hash = config.get("hydrogram", "api_hash", fallback=None)
    bot_token = config.get("hydrogram", "bot_token", fallback=None)
    return api_id, api_hash, bot_token


async def start_user_client(api_id, api_hash):
    user = Client(
        "user",
        workdir=".",
        api_id=api_id,
        api_hash=api_hash,
        plugins={"enabled": False},
    )
    await user.start()
    return user


async def get_user_session_data(user):
    config = get_config()
    session_config = {k: v for section in config.sections() for k, v in config.items(section)}
    session_config = json.dumps(session_config)
    session_config = b64encode(session_config)

    session_string = await user.export_session_string()

    me = await user.get_me()
    mention = f"@{me.username}" if me.username else me.first_name
    print(f"[green]- OK! Logged in as {mention}[/]")
    return session_config, session_string


def print_session_data(session_config, session_string):
    if __name__ == "__main__":
        print("\nYour PYROGRAM_CONFIG (SENSITIVE DATA, DO NOT SHARE):")
        print(f"[blue]{session_config}[/]")

        print("\nYour PYROGRAM_SESSION (SENSITIVE DATA, DO NOT SHARE):")
        print(f"[blue]{session_string}[/]\n")


async def check_existing_bot_session(api_id, api_hash, bot_token):
    login_bot = True
    if Path("bot.session").exists():
        async with Client(
            "bot",
            workdir=".",
            api_id=api_id,
            api_hash=api_hash,
            bot_token=bot_token,
            plugins={"enabled": False},
        ) as bot:
            me = await bot.get_me()
        mention = "@" + me.username
        print(
            rf"[bold yellow]I found an existing session from bot [/][cyan]{mention}[/]"
            rf"[bold yellow]. Do you want to use it? [/][cyan]\[yn]",
            end="",
        )
        c = click.getchar(True)
        login_bot = c == "n"
    return login_bot


async def login_assistant_bot(login_bot, api_id, api_hash, bot_token):
    print("\n[bold green]- Logging in the assistant bot...")
    if login_bot and Path("bot.session").exists():
        Path("bot.session").unlink()
    if "BOT_TOKEN" not in os.environ:
        text = "\n┌ [light_sea_green]BOT_TOKEN[/light_sea_green]"
        print(text)

        try:
            user_value = input("└> ")
        except (KeyboardInterrupt, EOFError):
            print("[red1]Operation cancelled by user")
            sys.exit()
        if not user_value:
            print("[red1]BOT_TOKEN is required, cannot be empty.")
            sys.exit()
        os.environ["BOT_TOKEN"] = user_value

    try:
        bot = Client(
            "bot",
            workdir=".",
            api_id=api_id,
            api_hash=api_hash,
            plugins={"enabled": False},
            bot_token=os.getenv("BOT_TOKEN"),
        )
        await bot.start()
    except hydrogram.errors.AccessTokenInvalid:
        print("[red1]The bot access token is invalid")
        sys.exit()

    me = await bot.get_me()
    print(f"[green]- OK! Registered @{me.username} as assistant bot.[/]")

    return bot


if __name__ == "__main__":
    asyncio.run(main())
