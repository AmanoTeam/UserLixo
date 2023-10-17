#!/usr/bin/env python3

# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

import os
import re
from pathlib import Path

import yaml
from langs import Langs
from rich import print

reserved = dir(Langs)
dir_path = Path(__file__).resolve().parent

lang_regex = re.compile(r"\blangs?\.(?P<key>\w+)")

all_keys = [
    match["key"]
    for root, directories, filenames in os.walk(".")
    for name in filenames
    if name.endswith(".py") and not re.search(r"(venv|\.git)/", str(Path(root) / name))
    for match in lang_regex.finditer((Path(root) / name).read_text())
]

# unique
all_keys = [*set(all_keys)]
all_keys = [x for x in all_keys if x not in reserved]


for strings_path in Path(dir_path).rglob("*.yml"):
    synced = True
    with Path(strings_path).open() as file:
        obj = yaml.safe_load(file)
        print(f"[blue]\n- {obj['NAME']} ({obj['LANGUAGE_CODE']})[/]")

    not_in_yml = [key for key in all_keys if key not in obj]
    for key in not_in_yml:
        to_write = f"\n{key}: |-\n    {key.upper()}\n"
        with Path(strings_path).open("a") as file:
            if file.write(to_write):
                synced = False
                print(f'[green]    New key "{key}" written into {Path(file.name).name}[/]')

    not_in_py = [key for key in obj if key not in all_keys and not key.isupper()]
    for key in not_in_py:
        synced = False
        print(f'[yellow]    The key "{key}" is not being used in any script[/]')

    if synced:
        print(f'[green]    The file "{Path(strings_path).name}" is already synced[/]')
