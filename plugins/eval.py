from pyrogram import Client, Filters

@Client.on_message(Filters.command("eval", prefixes=".") & Filters.me)
def seval(client, message):
    expression = message.text[6:]
    if expression:
        frass = f'**Eval Expression:**\n```{expression}```\n'
        message.edit(frass+'**Running...**')
        try:
            result = eval(expression)   
        except Exception as error:
            message.edit(frass+f'**Error:**\n```{error}```')
        else:
            if not result:
                message.edit(frass+'**Success**')
            else:
                message.edit(frass+f'**Result:**\n```{result}```')
