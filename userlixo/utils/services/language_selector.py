import glob
import os
import re

import yaml
from kink import inject
from langs import Langs


def open_yml(filename):
    with open(filename) as fp:
        data = yaml.safe_load(fp)
    return data


@inject
class LanguageSelector:
    def __init__(self):
        strings = {}
        for string_file in glob.glob("userlixo/strings/*.yml"):
            language_code = re.match(r"userlixo/strings/(.+)\.yml$", string_file)[1]
            strings[language_code] = open_yml(string_file)

        self.langs = Langs(**strings, escape_html=True)

    def get_lang(self):
        self.langs.code = os.environ["LANGUAGE"]
        return self.langs.get_language(os.getenv("LANGUAGE"))
