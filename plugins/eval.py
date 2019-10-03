from pyrogram import Client, Filters
from config import sudos

@Client.on_message(Filters.command("eval", prefixes="!"))
def seval(client, message):
    if message.from_user.id in sudos:
        expression = " ".join(message.command[1:])
        if expression:
            frass = f'**Eval Expression:**\n```{expression}```\n'
            m = message.reply(frass+'**Running...**')
            try:
                result = eval(expression)   
            except Exception as error:
                m.edit(frass+f'**Error:**\n```{error}```')
            else:
                if not result:
                    m.edit(frass+'**Success**')
                else:
                    m.edit(frass+f'**Result:**\n```{result}```')
