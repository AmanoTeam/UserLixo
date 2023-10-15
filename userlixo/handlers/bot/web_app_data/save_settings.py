import json
import os

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message, ReplyKeyboardRemove

from userlixo.config import sudoers, user
from userlixo.database import Config


@Client.on_message(filters.web_data_cmd("save_settings"))
async def upgrade(c: Client, m: Message):
    async def update_config(key, value):
        await Config.filter(key=key).update(value=value)
        os.environ[key] = value

    settings = json.loads(m.web_app_data.data.split("--", 1)[1])

    if "web_app_url" in settings:
        await update_config("WEB_APP_URL", settings["web_app_url"])
    if "logs_chat" in settings:
        await update_config("LOGS_CHAT", settings["logs_chat"])
    if "prefixes" in settings:
        await update_config("PREFIXES", settings["prefixes"])
    if "sudoers" in settings:
        await update_config("SUDOERS_LIST", settings["sudoers"])
        sudoers.clear()
        sudoers.append(user.me.id)
        sudoers.extend(settings["sudoers"].split(" "))
    if "language" in settings:
        await update_config("LANGUAGE", settings["language"])

    await m.reply(
        "The followings settings were set:\n" + json.dumps(settings, indent=2),
        reply_markup=ReplyKeyboardRemove(),
    )
