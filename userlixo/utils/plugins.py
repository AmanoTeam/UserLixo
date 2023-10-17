# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

import json
import os
import re
from configparser import ConfigParser
from pathlib import Path

from userlixo.database import Config


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
    with Path.open(filename) as f:
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
