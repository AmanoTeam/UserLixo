# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

import html
import re
from pathlib import Path

from pyrogram import Client, filters
from pyrogram.types import Message

from userlixo.utils.misc import shell_exec


@Client.on_message(filters.su_cmd(r"(?P<command>cmd|sh)\s+(?P<code>.+)", flags=re.S))
async def on_cmd_user(c: Client, m: Message):
    await cmd(c, m)


async def cmd(c: Client, m: Message):
    lang = m._lang
    act = m.edit if await filters.me(c, m) else m.reply

    code = m.matches[0]["code"]
    command = m.matches[0]["command"]

    result, process = await shell_exec(code)
    output = result or lang.executed_cmd

    if len(output) > 4096:
        with Path("output.txt").open("w") as f:
            f.write(str(output))
        await m.reply_document("output.txt", quote=True)
        return Path("output.txt").unlink()

    output = html.escape(str(output))  # escape html special chars

    text = "".join(f"<code>{line}</code>\n" for line in output.splitlines())
    if command == "cmd":
        return await act(text)
    await m.reply(text)
    return None
