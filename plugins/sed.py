import re

from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message

from utils import switch_case


@Client.on_message(
    filters.regex(r"\.?s/(?P<search>.+)/(?P<replace>.+)(?:/(?P<flags>.+))?")
    & filters.me
)
async def onsed(client: Client, message: Message):
    if (
        not message.reply_to_message
        or not message.reply_to_message.from_user
        or message.reply_to_message.from_user.id != (await client.get_me()).id
    ):
        return
    match = message.matches[0]
    flags = 0
    if match["flags"]:
        for flag in match["flags"]:
            flag = switch_case(
                flag.lower(),
                {
                    "i": re.I,
                    "s": re.S,
                    "m": re.M,
                    "a": re.A,
                    "l": re.L,
                    "x": re.X,
                },
            )
            if flag != None:
                flags |= flag
    text = message.reply_to_message.text.html
    text = re.sub(match["search"], match["replace"], text, 0, flags)
    await message.reply_to_message.edit(text, parse_mode=ParseMode.HTML)
