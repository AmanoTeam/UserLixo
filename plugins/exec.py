from pyrogram import Client, Filters
from config import sudos
from contextlib import redirect_stdout
import traceback
import io

@Client.on_message(Filters.command("exec", prefixes="!"))
def sexec(client, message):
    if message.from_user.id in sudos:
        expression = message.text[6:]
        if expression:
            frass = f'**Exec Expression:**\n```{expression}```\n'
            m = message.reply(frass+'**Running...**')
            try:
                with io.StringIO() as buf, redirect_stdout(buf):
                    exec(expression)
                    result = buf.getvalue()
            except:
                m.edit(frass+f'**Error:**\n```{traceback.format_exc()}```')
            else:
                if not result:
                    m.edit(frass+'**Success**')
                else:
                    m.edit(frass+f'**Result:**\n```{result}```')
