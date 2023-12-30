import os
import re
from pathlib import Path

import yaml
from kink import inject
from langs import Langs


@inject
class LanguageSelector:
    def __init__(self):
        strings = {}
        for file in Path().glob("userlixo/strings/*.yml"):
            language_code = re.search(r"(\w+)\.yml$", str(file)).group(1)

            with file.open(encoding="utf-8") as fp:
                strings[language_code] = yaml.safe_load(fp)

        self.langs = Langs(**strings, escape_html=True)

    def get_lang(self):
        self.langs.code = os.getenv("LANGUAGE") or "en"
        return self.langs.get_language(self.langs.code)
