# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

import importlib
import json
import re
import typing
from collections.abc import Callable
from pathlib import Path
from shutil import rmtree
from zipfile import ZipFile

import requirements
import toml
import virtualenv
from activate_virtualenv import activate_virtualenv
from rich.console import Console

from userlixo.config import bot, plugins, user
from userlixo.database import Config
from userlixo.types.handler_callable import HandlerCallable
from userlixo.types.plugin_element_collection import PluginElementCollection
from userlixo.types.plugin_info import PluginInfo
from userlixo.utils import shell_exec


async def get_inactive_plugins(plugins):
    inactive = (await Config.get_or_create({"value": "[]"}, key="INACTIVE_PLUGINS"))[0].value
    return json.loads(inactive)


console = Console()


class InvalidPluginInfoValueError(Exception):
    pass


def get_plugin_folder_path(plugin_name: str):
    return Path("userlixo/plugins") / plugin_name


def check_if_plugin_folder_exists(plugin_name: str):
    plugin_folder = get_plugin_folder_path(plugin_name)
    return plugin_folder.exists()


def unzip_plugin_to_folder(zip_path: str, plugin_name: str):
    folder_path = get_plugin_folder_path(plugin_name)
    with ZipFile(zip_path, "r") as zipfile:
        zipfile.extractall(str(folder_path))


def get_plugin_info_from_zip(zip_path: str) -> PluginInfo | None:
    with ZipFile(zip_path, "r") as zipfile:
        for file_name in zipfile.namelist():
            basename = Path(file_name).name
            if basename == "plugin.toml":
                content = zipfile.read(file_name).decode("utf-8")
                info = parse_plugin_info_from_toml(content)
                validate_plugin_info(info)
                if info:
                    info.zip_path = zip_path
                    return info
                return None
    return None


def get_plugin_info_from_folder(plugin_name: str) -> PluginInfo | None:
    folder_path = get_plugin_folder_path(plugin_name)
    if not (folder_path / "plugin.toml").exists():
        return None

    info_toml = (folder_path / "plugin.toml").read_text()
    info = parse_plugin_info_from_toml(info_toml)

    if info:
        info.folder_path = str(folder_path)

    validate_plugin_info(info)

    return info


def parse_plugin_info_from_toml(content: str) -> PluginInfo | None:
    parsed_toml = toml.loads(content)

    if "plugin" not in parsed_toml:
        return None

    return PluginInfo.from_dict(parsed_toml["plugin"])


def validate_plugin_info(info: PluginInfo | None):
    required = ["name", "description", "author"]
    console.log("info:", info)
    missing = [item for item in required if not getattr(info, item, None)]

    errors = []

    if missing:
        errors = [f"missing required field: {item}" for item in missing]
        raise InvalidPluginInfoValueError(errors)

    if info.name.strip() == "":
        errors.append("name cannot be empty")
    if not re.match(r"\w+$", info.name):
        errors.append("name must be alphanumeric")
    if (isinstance(info.author, str) and info.author.strip() == "") or (
        isinstance(info.author, list) and not len(info.author)
    ):
        errors.append("author cannot be empty")

    if errors:
        raise InvalidPluginInfoValueError(errors)


def parse_plugin_requirements_from_info(info: PluginInfo):
    if not info.requirements:
        return {}

    requirements_list = info.requirements
    parsed_dict = {}

    for item in requirements_list:
        if not isinstance(item, str):
            raise InvalidPluginInfoValueError(["requirements must be a list of strings"])

        try:
            parsed = requirements.parse(item)
        except ValueError as e:
            raise InvalidPluginInfoValueError([f"could not parse requirement {item}: {e}"])

        parsed = list(parsed)

        if not parsed or not len(parsed):
            raise InvalidPluginInfoValueError([f"could not parse requirement: {item}"])

        if len(parsed) > 1:
            raise InvalidPluginInfoValueError(
                [f"requirement {item} seems to refer to more than one package"]
            )

        parsed = parsed[0]

        if parsed.name in parsed_dict:
            raise InvalidPluginInfoValueError([f"requirement {item} is duplicated"])

        parsed_dict[parsed.name] = parsed

    return parsed_dict


def convert_parsed_requirements_to_pip_format(parsed_requirements: dict):
    return "\n".join([parsed.line for parsed in parsed_requirements.values()])


def write_plugin_requirements_txt(plugin_name: str) -> str:
    folder_path = get_plugin_folder_path(plugin_name)

    info = get_plugin_info_from_folder(plugin_name)

    requirements_txt_path = folder_path / "requirements.txt"
    if requirements_txt_path.exists():
        return str(requirements_txt_path)

    plugin_requirements = parse_plugin_requirements_from_info(info)
    pip_requirements = convert_parsed_requirements_to_pip_format(plugin_requirements)

    requirements_txt_path.write_text(pip_requirements)

    return str(requirements_txt_path)


async def install_plugin_requirements_in_its_venv(plugin_name: str):
    venv_path = await get_plugin_venv_path(plugin_name)
    requirements_txt_path = write_plugin_requirements_txt(plugin_name)

    stdout, process = await shell_exec(f"{venv_path}/bin/pip install -r {requirements_txt_path}")

    if process.returncode != 0:
        raise ValueError(f"Error while installing requirements: {stdout}")

    return stdout


async def get_plugin_venv_path(plugin_name: str, create_if_not_exists: bool = True):
    folder_path = get_plugin_folder_path(plugin_name)
    venv_path = str(folder_path / "venv")

    if create_if_not_exists and not Path(venv_path).exists():
        create_virtualenv(venv_path)

    return venv_path


def create_virtualenv(venv_path: str):
    virtualenv.cli_run([venv_path])


async def load_all_installed_plugins():
    for folder in Path().glob("userlixo/plugins/*"):
        if not folder.is_dir():
            continue

        try:
            plugin_name = folder.stem
            info = await load_plugin(plugin_name)
            plugins[info.name] = info
        except Exception:
            console.print_exception()


def filepath_to_notation(filepath: str):
    relative = Path(filepath).resolve().relative_to(Path.cwd()).with_suffix("")
    return str(relative).replace("/", ".")


def import_module_from_filepath(filepath: str):
    notation = filepath_to_notation(filepath)
    return importlib.import_module(notation)


def fetch_plugin_elements(plugin_name: str) -> PluginElementCollection | None:
    folder_path = get_plugin_folder_path(plugin_name)
    try:
        module = import_module_from_filepath(str(folder_path))
    except Exception:
        console.print_exception()
        return None

    user_controllers = []
    bot_controllers = []

    user_handlers: list[HandlerCallable] = []
    bot_handlers: list[HandlerCallable] = []

    pre_load: list[Callable] = []
    post_load: list[Callable] = []

    for f in module.__dict__.values():
        if callable(f):
            if hasattr(f, "is_pre_load"):
                pre_load.append(f)
            if hasattr(f, "is_post_load"):
                post_load.append(f)
            if hasattr(f, "is_user_plugin_handler"):
                f = typing.cast(HandlerCallable, f)
                user_handlers.append(f)
            if hasattr(f, "is_bot_plugin_handler"):
                f = typing.cast(HandlerCallable, f)
                bot_handlers.append(f)
        elif hasattr(f, "is_user_plugin_controller"):
            user_controllers.append(f)
        elif hasattr(f, "is_bot_plugin_controller"):
            bot_controllers.append(f)

    return PluginElementCollection(
        pre_load=pre_load,
        post_load=post_load,
        user_handlers=user_handlers,
        bot_handlers=bot_handlers,
        user_controllers=user_controllers,
        bot_controllers=bot_controllers,
    )


def validate_plugin_folder(plugin_name: str):
    folder_path = get_plugin_folder_path(plugin_name)

    if not folder_path.is_dir():
        raise ValueError(f"Invalid folder path: {folder_path} is not a folder")

    if not (folder_path / "__init__.py").exists():
        raise ValueError(f"Invalid folder path: __init__.py is missing at folder {folder_path}")

    if not (folder_path / "plugin.toml").exists():
        raise ValueError(f"Invalid folder path: plugin.toml is missing at folder {folder_path}")


async def load_plugin(plugin_name: str):
    validate_plugin_folder(plugin_name)

    info = get_plugin_info_from_folder(plugin_name)
    validate_plugin_info(info)

    venv_path = await get_plugin_venv_path(plugin_name)
    await install_plugin_requirements_in_its_venv(plugin_name)

    with activate_virtualenv(venv_path):
        elements = fetch_plugin_elements(plugin_name)
    load_plugin_elements(elements)

    return info


def load_plugin_elements(elements: PluginElementCollection):
    if elements.pre_load:
        for f in elements.pre_load:
            f()

    if elements.user_handlers:
        for handler in elements.user_handlers:
            for h in handler.handlers:
                console.log(f"Adding handler {h} for user")
                user.add_handler(*h)

    if elements.bot_handlers:
        for handler in elements.bot_handlers:
            for h in handler.handlers:
                console.log(f"Adding handler {h} for bot")
                bot.add_handler(*h)

    if elements.user_controllers:
        for controller in elements.user_controllers:
            controller.__controller__.register(user)

    if elements.bot_controllers:
        for controller in elements.bot_controllers:
            controller.__controller__.register(bot)

    if elements.post_load:
        for f in elements.post_load:
            f()


async def unload_and_remove_plugin(plugin_name: str):
    folder_path = get_plugin_folder_path(plugin_name)
    await unload_plugin(plugin_name)

    rmtree(str(folder_path))


async def unload_plugin(plugin_name: str):
    validate_plugin_folder(plugin_name)

    info = get_plugin_info_from_folder(plugin_name)
    validate_plugin_info(info)

    venv_path = await get_plugin_venv_path(plugin_name)
    with activate_virtualenv(venv_path):
        elements = fetch_plugin_elements(plugin_name)
    unload_each_plugin_element(elements)


def unload_each_plugin_element(elements: PluginElementCollection):
    if elements.user_handlers:
        for handler in elements.user_handlers:
            for h in handler.handlers:
                console.log(f"Removing handler {h} for user")
                user.remove_handler(*h)

    if elements.bot_handlers:
        for handler in elements.bot_handlers:
            for h in handler.handlers:
                console.log(f"Removing handler {h} for bot")
                bot.remove_handler(*h)

    if elements.user_controllers:
        for controller in elements.user_controllers:
            controller.__controller__.unregister(user)

    if elements.bot_controllers:
        for controller in elements.bot_controllers:
            controller.__controller__.unregister(bot)
