import io
import traceback
from contextlib import redirect_stdout

from pyrogram import Client, Filters


@Client.on_message(Filters.command("exec", prefixes=".") & Filters.me)
async def sexec(client, message):
    expression = message.text[6:]
    if expression:
        frass = f'**Exec Expression:**\n```{expression}```\n'
        m = await message.reply(frass + '**Running...**')
        try:
            with io.StringIO() as buf, redirect_stdout(buf):
                exec(expression)
                result = buf.getvalue()
        except:
            await m.edit(frass + f'**Error:**\n```{traceback.format_exc()}```')
        else:
            if not result:
                await m.edit(frass + '**Success**')
            else:
                await m.edit(frass + f'**Result:**\n```{result}```')
