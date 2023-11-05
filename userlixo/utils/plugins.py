# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

import importlib
import json
import os
import re
from configparser import ConfigParser
from pathlib import Path
from zipfile import ZipFile

import requirements
import toml
import virtualenv
from activate_virtualenv import activate_virtualenv
from rich.console import Console

from userlixo.config import bot, user
from userlixo.database import Config
from userlixo.utils import shell_exec


async def get_inactive_plugins(plugins):
    inactive = (await Config.get_or_create({"value": "[]"}, key="INACTIVE_PLUGINS"))[0].value
    return json.loads(inactive)


def reload_plugins_requirements(plugins):
    old_requirements = []
    if Path("plugins-requirements.txt").exists():
        with Path("plugins-requirements.txt").open() as f:
            old_requirements = [x for x in f.read().split("\n") if len(x)]
    requirements = []
    for items in plugins.values():
        for p in items.values():
            p_requires = p.get("requirements", "")
            p_requires = re.split("[, ]{1,}", p_requires)
            requirements.extend(p_requires)
    with Path("plugins-requirements.txt").open("w") as f:
        f.write("\n".join(requirements))
    unused = list(set(old_requirements) - set(requirements))
    return requirements, unused


def write_plugin_info(plugins, lang, info, **kwargs):
    lang.escape_html = False
    info_lines = {"status_line": "", "requirements_line": ""}
    for item in ["channel", "github", "contributors", "type"]:
        text = ""
        if item in info:
            text = getattr(lang, f"plugin_{item}_line")
            text = "\n" + text(**{item: info[item]})
        info_lines[item + "_line"] = text

    lang.escape_html = True
    if "requirements" in info:
        info_lines["requirements_line"] = "\n" + lang.plugin_requirements_line(
            requirements=info["requirements"]
        )

    text = lang.plugin_info
    text.escape_html = False
    return text(
        info=info,
        **{**info_lines, **kwargs},  # make kwargs override info_lines
    )


def read_plugin_info(filename):
    with Path(filename).open() as f:
        data = f.read()
    if not (
        match := re.search(
            r'"""\s*(?P<title>.+?)\n\n(?P<description>.+?)\n\n(?P<ini>.+?)\s*"""',
            data,
            re.DOTALL,
        )
    ):
        return None

    notation = re.sub(r"\.py$", "", os.path.relpath(filename)).replace("/", ".")
    basename = Path(filename)
    values = ConfigParser()
    values.read_string("[doc]\n" + match["ini"])
    values = values._sections["doc"]

    default = {"author": "?"}
    default.update(values)
    values = default

    plugin_type = values.get("type", "user")
    if plugin_type not in ("user", "bot"):
        plugin_type = "user"

    return {
        "basename": basename,
        "type": plugin_type,
        "title": match["title"],
        "description": match["description"],
        "filename": filename,
        "notation": notation,
        **values,
    }


console = Console()


def filepath_to_plugin_name(filepath: str):
    relative = Path(filepath).resolve().relative_to(Path.cwd())
    path_with_dots = str(relative).replace("/", ".")
    return re.sub(r"\.py$", "", path_with_dots)


def import_module_from_filepath(filepath: str):
    notation = filepath_to_plugin_name(filepath)
    return importlib.import_module(notation)


def fetch_plugin_elements_from_file(filename: str):
    try:
        module = import_module_from_filepath(filename)
    except Exception:
        console.print_exception()
        return None

    user_controllers = []
    bot_controllers = []

    user_handlers = []
    bot_handlers = []

    pre_load = []
    post_load = []

    for f in module.__dict__.values():
        if callable(f):
            if hasattr(f, "is_pre_load"):
                pre_load.append(f)
            if hasattr(f, "is_post_load"):
                post_load.append(f)
            if hasattr(f, "is_user_plugin_handler"):
                user_handlers.append(f)
            if hasattr(f, "is_bot_plugin_handler"):
                bot_handlers.append(f)
        elif hasattr(f, "is_user_plugin_controller"):
            user_controllers.append(f)
        elif hasattr(f, "is_bot_plugin_controller"):
            bot_controllers.append(f)

    return {
        "pre_load": pre_load,
        "post_load": post_load,
        "user_handlers": user_handlers,
        "bot_handlers": bot_handlers,
        "user_controllers": user_controllers,
        "bot_controllers": bot_controllers,
    }


def load_plugin_elements(elements: dict):
    if "pre_load" in elements:
        for f in elements["pre_load"]:
            f()

    if "user_handlers" in elements:
        for handler in elements["user_handlers"]:
            for h in handler.handlers:
                console.log(f"Adding handler {h} for user")
                user.add_handler(*h)

    if "bot_handlers" in elements:
        for handler in elements["bot_handlers"]:
            for h in handler.handlers:
                console.log(f"Adding handler {h} for bot")
                bot.add_handler(*h)

    if "user_controllers" in elements:
        for controller in elements["user_controllers"]:
            controller.__controller__.register(user)

    if "bot_controllers" in elements:
        for controller in elements["bot_controllers"]:
            controller.__controller__.register(bot)

    if "post_load" in elements:
        for f in elements["post_load"]:
            f()


class MissingPluginInfoError(Exception):
    pass


class InvalidPluginInfoValueError(Exception):
    pass


def validate_plugin_info(info: dict):
    required = ["title", "description", "author"]
    missing = [item for item in required if item not in info]

    if missing:
        raise MissingPluginInfoError(", ".join(missing))

    errors = []
    if info["title"].strip() == "":
        errors.append("title cannot be empty")
    if not re.match(r"\w+$", info["title"]):
        errors.append("title must be alphanumeric")
    if info["author"].strip() == "":
        errors.append("author cannot be empty")

    if errors:
        raise InvalidPluginInfoValueError(errors)


def get_plugin_info_from_zip(zip_path: str):
    with ZipFile(zip_path, "r") as zipfile:
        for file_name in zipfile.namelist():
            if file_name.endswith(".toml"):
                content = zipfile.read(file_name).decode("utf-8")
                info = parse_plugin_info_from_toml(content)
                if info:
                    return info
    return None


def parse_plugin_info_from_toml(content: str):
    parsed_toml = toml.loads(content)

    if "plugin" not in parsed_toml:
        return None

    return parsed_toml["plugin"]


def parse_plugin_requirements_from_info(info: dict):
    if "requirements" not in info:
        return {}

    if not isinstance(info["requirements"], list):
        raise InvalidPluginInfoValueError(["requirements must be a list"])

    requirements_list = info["requirements"]
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


def save_plugin_requirements_info_requirements_txt(plugin_folder_path: str):
    folder = Path(plugin_folder_path)
    info_toml = (folder / "plugin.toml").read_text()
    info = parse_plugin_info_from_toml(info_toml)

    requirements_txt_path = Path(plugin_folder_path) / "requirements.txt"
    if requirements_txt_path.exists():
        return str(requirements_txt_path)

    plugin_requirements = parse_plugin_requirements_from_info(info)
    pip_requirements = convert_parsed_requirements_to_pip_format(plugin_requirements)

    requirements_txt_path.write_text(pip_requirements)

    return str(requirements_txt_path)


async def install_plugin_requirements_in_its_venv(plugin_folder_path: str):
    venv_path = await get_plugin_venv_path(plugin_folder_path)
    requirements_txt_path = save_plugin_requirements_info_requirements_txt(plugin_folder_path)

    stdout, process = await shell_exec(f"{venv_path}/bin/pip install -r {requirements_txt_path}")

    if process.returncode != 0:
        raise ValueError(f"Error while installing requirements: {stdout}")

    return stdout


def validate_plugin_folder(folder_path: str):
    folder = Path(folder_path)
    if not folder.is_dir():
        raise ValueError(f"Invalid folder path: {folder_path} is not a folder")

    if not (folder / "__init__.py").exists():
        raise ValueError(f"Invalid folder path: __init__.py is missing at folder {folder_path}")

    if not (folder / "plugin.toml").exists():
        raise ValueError(f"Invalid folder path: plugin.toml is missing at folder {folder_path}")


async def load_plugin_by_folder_path(folder_path: str):
    validate_plugin_folder(folder_path)

    folder = Path(folder_path)
    info_toml = (folder / "plugin.toml").read_text()
    info = parse_plugin_info_from_toml(info_toml)

    validate_plugin_info(info)

    venv_path = await get_plugin_venv_path(folder_path)
    await install_plugin_requirements_in_its_venv(folder_path)

    with activate_virtualenv(venv_path):
        main_file = str(folder / "__init__.py")
        elements = fetch_plugin_elements_from_file(main_file)
        console.log(f"Loading elements from plugin {info['title']}:", elements)
    load_plugin_elements(elements)


async def get_plugin_venv_path(plugin_folder_path: str, create_if_not_exists: bool = True):
    plugin_folder = Path(plugin_folder_path)
    venv_path = str(plugin_folder / "venv")

    if create_if_not_exists and not Path(venv_path).exists():
        create_virtualenv_on_plugin_folder(plugin_folder_path)

    return venv_path


def create_virtualenv_on_plugin_folder(folder_path: str):
    venv_path = str(Path(folder_path) / "venv")
    virtualenv.cli_run([venv_path])


async def load_all_installed_plugins():
    console.log("Loading all installed plugins...")
    console.log(Path().glob("userlixo/plugins/*"))
    for folder in Path().glob("userlixo/plugins/*"):
        if not folder.is_dir():
            continue

        console.log(f"Found plugin folder: {folder}")
        try:
            await load_plugin_by_folder_path(str(folder))
        except Exception:
            console.print_exception()
