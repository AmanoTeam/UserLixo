import os
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import Message
from config import bot
from locales import use_lang

import utils

@Client.on_message(filters.command("backup", prefixes=".") & filters.sudoers)
@use_lang()
async def backup(c: Client, m: Message, t):
    await m.edit(t("initiating_backup"))
    d1 = datetime.now()
    arq = await utils.backup_sources()
    await m.edit(t("uploading_backup"))
    await bot.send_document(
        chat_id=c.me.id,
        document=arq,
        caption=t("backup_caption").format(name=m.from_user.mention, date=d1),
    )
    d2 = datetime.now()
    await m.edit(t("backup_completed").format(time=(d2 - d1).seconds))
    os.remove(arq)
