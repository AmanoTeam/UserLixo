from pyrogram import Client, Filters
import re

@Client.on_message(Filters.regex(r'[\s\S]*\<py\>[\s\S]+\</py\>') & Filters.me)
async def pytag(client, message):
    for match in re.finditer(r'\<py\>(.+?)\</py\>', message.text):
        strio = io.StringIO()
        code = match[1].strip()
        exec('async def __ex(client, message): ' + ' '.join('\n ' + l for l in code.split('\n')))
        with redirect_stdout(strio):
            try:
                await locals()["__ex"](client, message)
            except:
                return await message.reply_text(html.escape(traceback.format_exc()), parse_mode="HTML")
    
        if strio.getvalue():
            out = f"{html.escape(strio.getvalue())}"
        else:
            out = "<py></py>"
        message.text = message.text.replace(match[0], out)