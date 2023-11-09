# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team
import importlib
import json
import logging
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

from userlixo.config import bot, plugins, user
from userlixo.database import Config, PluginSetting
from userlixo.types.client import Client
from userlixo.types.handler_callable import HandlerCallable
from userlixo.types.plugin_element_collection import PluginElementCollection
from userlixo.types.plugin_info import PluginInfo
from userlixo.types.plugin_settings import PluginSettings
from userlixo.utils import shell_exec
from userlixo.utils.validation import ValidateSetting

logger = logging.getLogger(__name__)


async def get_inactive_plugins(plugins):
    inactive = (await Config.get_or_create({"value": "[]"}, key="INACTIVE_PLUGINS"))[0].value
    return json.loads(inactive)


class InvalidPluginInfoValueError(ValueError):
    pass


class InvalidPluginSettingsValueError(ValueError):
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

    settings = parsed_toml.get("settings", None)

    return PluginInfo().fill_info(parsed_toml["plugin"]).fill_settings(settings)


def validate_plugin_info(info: PluginInfo | None):
    required = ["name", "description", "author"]
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

    try:
        if info.settings:
            validate_plugin_settings(info.settings)
    except InvalidPluginSettingsValueError as e:
        errors.extend([f"settings: {k}: {v}" for k, v in e.args[0].items()])

    if errors:
        raise InvalidPluginInfoValueError(errors)


def validate_plugin_settings(settings_dict: dict[str, PluginSettings]):
    all_errors = {}

    for k, v in settings_dict.items():
        errors = []

        errors.extend(ValidateSetting(v).check())

        all_errors[k] = errors

    if any(len(v) for v in all_errors.values()):
        raise InvalidPluginSettingsValueError(all_errors)


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


async def get_plugin_venv_path(
    plugin_name: str, create_if_not_exists: bool = True, overwrite_if_exists: bool = False
):
    folder_path = get_plugin_folder_path(plugin_name)
    venv_path = str(folder_path / "venv")

    if create_if_not_exists and not Path(venv_path).exists():
        create_virtualenv(venv_path)
    elif overwrite_if_exists:
        rmtree(venv_path)
        create_virtualenv(venv_path)

    return venv_path


def create_virtualenv(venv_path: str):
    virtualenv.cli_run([venv_path])


async def load_settings_values_for_plugin(plugin_name: str):
    plugin_info = plugins.get(plugin_name, None)
    if not plugin_info:
        return
    settings = await PluginSetting.filter(plugin=plugin_name).all()

    for setting in settings:
        if setting.key not in plugin_info.settings:
            continue

        plugin_info.settings[setting.key].value = setting.value


async def load_all_installed_plugins():
    inactive = await get_inactive_plugins(plugins)

    for folder in Path().glob("userlixo/plugins/*"):
        if not folder.is_dir():
            continue

        plugin_name = folder.stem
        if plugin_name in inactive:
            try:
                info = get_plugin_info_from_folder(plugin_name)
                validate_plugin_info(info)

                if info:
                    plugins[info.name] = info
                    await load_settings_values_for_plugin(info.name)

            except Exception as e:
                logger.exception("Error while loading inactive plugin", exc_info=e)
            continue

        try:
            info = await load_plugin(plugin_name)
            plugins[info.name] = info
        except Exception as e:
            logger.exception("Error while loading plugin", exc_info=e)


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
    except Exception as e:
        logger.exception("Error while importing plugin", exc_info=e)
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
            if hasattr(f, "is_user_plugin_controller"):
                user_controllers.append(f)
            if hasattr(f, "is_bot_plugin_controller"):
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
    load_plugin_elements(elements, plugin_name)

    return info


def load_plugin_elements(elements: PluginElementCollection, plugin_name: str):
    if elements.pre_load:
        for f in elements.pre_load:
            f()

    if elements.user_handlers:
        for handler in elements.user_handlers:
            for item in handler.handlers:
                h, group = item
                h.plugin_handler = plugin_name
                user.add_handler(h, group)

    if elements.bot_handlers:
        for handler in elements.bot_handlers:
            for item in handler.handlers:
                h, group = item
                h.plugin_handler = plugin_name
                user.add_handler(h, group)

    if elements.user_controllers:
        for controller in elements.user_controllers:
            controller.__controller__.register(user, plugin_handler=plugin_name)

    if elements.bot_controllers:
        for controller in elements.bot_controllers:
            controller.__controller__.register(bot, plugin_handler=plugin_name)

    if elements.post_load:
        for f in elements.post_load:
            f()


async def unload_and_remove_plugin(plugin_name: str):
    await unload_plugin(plugin_name)

    folder_path = get_plugin_folder_path(plugin_name)
    rmtree(str(folder_path))


async def unload_plugin(plugin_name: str):
    validate_plugin_folder(plugin_name)

    remove_plugin_handlers(plugin_name, user)
    remove_plugin_handlers(plugin_name, bot)


def remove_plugin_handlers(plugin_name: str, client: Client):
    for handlers in client.dispatcher.groups.values():
        for handler in handlers:
            if hasattr(handler, "plugin_handler") and handler.plugin_handler == plugin_name:
                handlers.remove(handler)
