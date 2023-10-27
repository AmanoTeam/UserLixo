import os
import re
from pathlib import Path

import yaml
from kink import inject
from langs import Langs


def open_yml(filename):
    with Path(filename).open() as fp:
        return yaml.safe_load(fp)


@inject
class LanguageSelector:
    def __init__(self):
        strings = {}
        for file in Path().glob("userlixo/strings/*.yml"):
            string_file = "userlixo/strings/" + file.name
            language_code = re.match(r"userlixo/strings/(.+)\.yml$", string_file).group(1)
            strings[language_code] = open_yml(string_file)

        self.langs = Langs(**strings, escape_html=True)

    def get_lang(self):
        self.langs.code = os.getenv("LANGUAGE") or "en"
        return self.langs.get_language(self.langs.code)
