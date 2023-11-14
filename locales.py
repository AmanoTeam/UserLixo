import yaml
from db import Config
from functools import partial, wraps
from glob import glob
import os
from typing import Dict, List
import inspect

langs = [
    "en-US",
    "pt-BR",
]

default_language = "pt-BR"

def cache_localizations(files: List[str]) -> Dict[str, Dict[str, Dict[str, str]]]:
    ldict = {lang: {} for lang in langs}
    for file in files:
        _, pname = file.split(os.path.sep)
        lang = pname.split(".")[0]
        with open(file, "r") as f:
            ldict[lang] = yaml.safe_load(f)
    return ldict

jsons = []

for locale in langs:
    jsons += glob(os.path.join("locales", f"{locale}.yml"))

langdict = cache_localizations(jsons)

def use_lang():

    def decorator(func):
        @wraps(func)
        async def wrapper(client, message):
            lang = await Config.get_or_none(id="lang")
            if not lang:
                lang = default_language
                await Config.create(id="lang", value=default_language)
            else:
                lang = lang.value

            lfunc = partial(get_locale_string, lang)
            return await func(client, message, lfunc)

        return wrapper

    return decorator

def get_locale_string(
    language: str, key: str
) -> str:
    res: str = (
        langdict[language].get(key) or key
    )
    return res
