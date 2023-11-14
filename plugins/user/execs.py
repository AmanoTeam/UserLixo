import html
import io
import re
import traceback
from contextlib import redirect_stdout

from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message
from locales import use_lang

@Client.on_message(filters.command("exec", prefixes=".") & filters.sudoers)
@use_lang()
async def execs(client: Client, message: Message, t):
    strio = io.StringIO()
    code = re.split(r"[\n ]+", message.text, 1)[1]
    exec(
        "async def __ex(client: Client, message: Message): "
        + " ".join("\n " + l for l in code.split("\n"))
    )
    with redirect_stdout(strio):
        try:
            await locals()["__ex"](client, message)
        except:
            return await message.reply_text(
                html.escape(traceback.format_exc()), parse_mode=ParseMode.HTML
            )

    if strio.getvalue():
        out = f"<code>{html.escape(strio.getvalue())}</code>"
    else:
        out = t("exec_seucess")
    await message.edit(out, parse_mode=ParseMode.HTML)

