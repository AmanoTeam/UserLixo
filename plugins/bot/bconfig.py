from functools import partial
from typing import Union

from hydrogram import Client, filters
from hydrogram.helpers import ikb
from hydrogram.types import CallbackQuery, Message

from config import plugins
from db import Config
from locales import get_locale_string, langdict, use_lang


@Client.on_message(filters.command("config") & filters.sudoers)
@Client.on_callback_query(filters.regex(r"\bconfig\b") & filters.sudoers)
@use_lang()
async def config(c: Client, m: Union[Message, CallbackQuery], t):
    keyb = [
        [(t("lang"), "config_lang")],
        [(t("plugins_settings_button"), "config_plugins")],
    ]

    if isinstance(m, Message):
        await m.reply(t("config_choose"), reply_markup=ikb(keyb))
    elif isinstance(m, CallbackQuery):
        await m.edit(t("config_choose"), reply_markup=ikb(keyb))


@Client.on_callback_query(filters.regex(r"^config_lang") & filters.sudoers)
@use_lang()
async def config_lang(c: Client, m: CallbackQuery, t):
    langs = list(langdict)
    keyb = [
        [
            (
                f"{langdict[lang]['FLAG']} {langdict[lang]['NAME']}",
                f"config_setlang_{langdict[lang]['LANGUAGE_CODE']}",
            )
        ]
        for lang in langs
    ]
    keyb.append([(t("back"), "config")])
    await m.edit(t("choose_lang"), reply_markup=ikb(keyb))


@Client.on_callback_query(filters.regex(r"^config_setlang_") & filters.sudoers)
@use_lang()
async def config_lang_cq(c: Client, m: CallbackQuery, t):
    lang = m.data.split("_", 2)[2]
    await Config.get(id="lang").update(value=lang)
    lfunc = partial(get_locale_string, lang)
    await m.edit(
        lfunc("lang_set"), reply_markup=ikb([[(lfunc("back"), "config_lang")]])
    )


@Client.on_callback_query(filters.regex(r"^config_plugins") & filters.sudoers)
@use_lang()
async def config_plugins(c: Client, m: CallbackQuery, t):
    table = []
    row = []
    for i, plugin in enumerate(plugins):
        if i % 2 == 0 and i != 0:
            table.append(row)
            row = []
        row.append((t(f"{plugin}_config_button"), f"config_plugin_{plugin}"))
    table.append(row)

    table.append([(t("back"), "config")])

    await m.edit(t("plugins_settings"), reply_markup=ikb(table))
