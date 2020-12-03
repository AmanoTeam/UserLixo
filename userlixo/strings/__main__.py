#!/usr/bin/env python3

import os
import re
import yaml

from glob import glob
from langs import Langs
from rich import print

reserved = dir(Langs)
dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path = dir_path.rstrip('/')

lang_regex = re.compile(r'\blangs?\.(?P<key>\w+)')
all_keys = []

for root, directories, filenames in os.walk('.'):
    for name in filenames:
        if not name.endswith('.py') or re.search('(venv|\.git)/', os.path.join(root, name)):
            continue
        with open(os.path.join(root, name)) as fp:
            contents = fp.read()
        for match in lang_regex.finditer(contents):
            all_keys.append(match['key'])

#unique
all_keys = [*set(all_keys)]
all_keys = [x for x in all_keys if x not in reserved]

for strings_path in glob(dir_path+'/*.yml'):
    synced = True
    with open(strings_path) as file:
        obj = yaml.safe_load(file)
        print(f"[blue]\n- {obj['NAME']} ({obj['LANGUAGE_CODE']})[/]")
    
    not_in_yml = [key for key in all_keys if key not in obj.keys()]
    for key in not_in_yml:
        to_write =f"\n{key}: |-\n    {key.upper()}\n"
        with open(strings_path, 'a') as file:
            if file.write(to_write):
                synced = False
                print(f'[green]    New key "{key}" written into {os.path.basename(file.name)}[/]')
    
    not_in_py = [key for key in obj.keys() if key not in all_keys and not key.isupper()]
    for key in not_in_py:
        synced = False
        print(f'[yellow]    The key "{key}" is not being used in any script[/]')
    
    if synced:
        print(f'[green]    The file "{os.path.basename(strings_path)}" is already synced[/]')