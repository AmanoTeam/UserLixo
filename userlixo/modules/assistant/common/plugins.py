import importlib
import re
from pathlib import Path
from zipfile import ZipFile

import toml
import virtualenv
from langs import Langs
from pyrogram.helpers import ikb
from pyrogram.nav import Pagination

from userlixo.config import bot, plugins, user
from userlixo.utils.plugins import (
    get_inactive_plugins,
    write_plugin_info,
)


def filepath_to_plugin_name(filepath: str):
    relative = Path(filepath).resolve().relative_to(Path.cwd())
    path_with_dots = str(relative).replace("/", ".")
    return re.sub(r"\.py$", "", path_with_dots)


def import_module_from_filepath(filepath: str):
    notation = filepath_to_plugin_name(filepath)
    return importlib.import_module(notation)


def fetch_elements_from_file(filename: str):
    try:
        module = import_module_from_filepath(filename)
    except Exception as e:
        print(e)
        return None

    controllers = []
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
        elif hasattr(f, "is_controller"):
            controllers.append(f)

    return {
        "pre_load": pre_load,
        "post_load": post_load,
        "user_handlers": user_handlers,
        "bot_handlers": bot_handlers,
        "controllers": controllers,
    }


def load_plugin_elements(elements: dict):
    if "pre_load" in elements:
        for f in elements["pre_load"]:
            f()

    if "user_handlers" in elements:
        for handler in elements["user_handlers"]:
            user.add_handler(handler)

    if "bot_handlers" in elements:
        for handler in elements["bot_handlers"]:
            bot.add_handler(handler)

    if "controllers" in elements:
        for controller in elements["controllers"]:
            controller.load()

    if "post_load" in elements:
        for f in elements["post_load"]:
            f()


class MissingPluginInfoError(Exception):
    pass


class InvalidPluginInfoValueError(Exception):
    pass


def validate_plugin_info(info: dict):
    required = ["title", "description", "author", "type"]
    missing = [item for item in required if item not in info]

    if missing:
        raise MissingPluginInfoError("', '.join(missing)")

    errors = []
    if info["title"].strip() == "":
        errors.append("title cannot be empty")
    if re.match(r"\w+$", info["title"]):
        errors.append("title must be alphanumeric")
    if info["author"].strip() == "":
        errors.append("author cannot be empty")
    if info["type"] not in ("user", "bot"):
        errors.append("type must be 'user' or 'bot'")

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


def validate_plugin_folder(folder_path: str):
    folder = Path(folder_path)
    if not folder.is_dir():
        raise ValueError(f"Invalid folder path: {folder_path} is not a folder")

    if not (folder / "__init__.py").exists():
        raise ValueError(f"Invalid folder path: __init__.py is missing at folder {folder_path}")

    if not (folder / "plugin.toml").exists():
        raise ValueError(f"Invalid folder path: plugin.toml is missing at folder {folder_path}")


def load_plugin_by_folder_path(folder_path: str):
    validate_plugin_folder(folder_path)

    folder = Path(folder_path)
    info_toml = (folder / "plugin.toml").read_text()
    info = parse_plugin_info_from_toml(info_toml)

    validate_plugin_info(info)

    main_file = str(folder / "__init__.py")
    elements = fetch_elements_from_file(main_file)
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


async def compose_list_plugins_by_type_message(
    lang: Langs,
    plugin_type: str,
    page: int,
    show_add_plugin_button: bool = True,
    append_back: bool = False,
):
    inactive_plugins = await get_inactive_plugins(plugins)

    def item_title(i, _pg):
        name = i[0]
        notation = i[1]["notation"]
        status = "💤" if notation in inactive_plugins else "❇️"
        return f"{status} {name}"

    layout = Pagination(
        [*plugins[plugin_type].items()],
        item_data=lambda i, pg: f"info_plugin {i[0]} {plugin_type} {pg}",
        item_title=item_title,
        page_data=lambda pg: f"{plugin_type}_plugins {pg}",
    )

    lines = layout.create(page, lines=4, columns=2)

    # if the message is /plugins (sent to bot) or it's a callback query 'plugins'
    if show_add_plugin_button:
        lines.append([(lang.add_plugin, f"add_plugin {page}")])
    else:  # is command to user
        lines.append([(lang.add_plugin, f"t.me/{bot.me.username}?start=plugin_add", "url")])

    if append_back:
        lines.append([(lang.back, "list_plugins")])
    keyboard = ikb(lines)
    return lang.plugins_text(type=plugin_type), keyboard


async def compose_info_plugin_message(
    lang: Langs, plugin_type: str, plugin_basename: str, page: int
):
    plugin = plugins[plugin_type][plugin_basename]

    status = lang.active
    first_btn = (
        lang.deactivate,
        f"deactivate_plugin {plugin_basename} {plugin_type} {page}",
    )

    inactive = await get_inactive_plugins(plugins)

    if plugin["notation"] in inactive:
        status = lang.inactive
        first_btn = (
            lang.activate,
            f"activate_plugin {plugin_basename} {plugin_type} {page}",
        )
    status_line = "\n" + status

    lines = [
        [
            first_btn,
            (lang.remove, f"remove_plugin {plugin_basename} {plugin_type} {page}"),
        ]
    ]
    if plugin.get("settings"):
        lines.append([(lang.settings, f"plugin_settings {plugin_basename} {plugin_type} {page}")])
    lines.append([(lang.back, f"{plugin_type}_plugins {page}")])
    keyboard = ikb(lines)

    text = write_plugin_info(plugins, lang, plugin, status_line=status_line)

    return text, keyboard
