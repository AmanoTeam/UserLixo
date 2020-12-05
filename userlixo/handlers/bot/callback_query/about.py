from pyrogram import Client, filters
from pyromod.helpers import ikb
from userlixo.config import cmds
import os

@Client.on_callback_query(filters.sudoers & filters.regex('^about_(?P<subject>userlixo|plugins|commands)'))
async def on_about_userlixo(c, cq):
    lang = cq._lang
    subject = cq.matches[0]['subject']
    keyboard = ikb([
        [(lang.back, 'help')]
    ])
    text = {
        "userlixo": lang.about_userlixo_text,
        "plugins": lang.about_plugins_text,
        "commands": lang.about_commands_text
    }
    text = text[subject]
    if subject == 'commands':
        commands = [*cmds.keys()]
        total = len(commands)
        prefixes = os.getenv('PREFIXES')
        examples = []
        for n,p in enumerate([*prefixes]):
            if n > total-1: # if passed the end
                break
            examples.append('<code>'+p+commands[n]+'</code>')
        examples = ', '.join(examples)
        commands_list = [*map(lambda x: f'<code>{x}</code>', commands)]
        
        text.escape_html = False
        text = text(
            total=total,
            commands=', '.join(commands_list[:-1]),
            last_command=commands_list[-1],
            prefixes=prefixes,
            examples=examples
        )
    await cq.edit(text, keyboard, disable_web_page_preview=True)