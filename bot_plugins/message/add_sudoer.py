import re
from config import sudoers
from database import Config
from pyrogram import Client, Filters

@Client.on_message(Filters.su_cmd('^/(start )?add_sudoer'))
async def on_add_sudoer(client, message):
    lang = message.lang
    text = lang.add_sudoer_ask
    response = await message.chat.ask(text, Filters.text, 600)
    
    if not re.match(r'@?\w+$', response.text):
        return await message.reply(lang.add_sudoer_not_match)
    
    sudoers.append(response.text.lstrip('@'))
    await Config.get(key='SUDOERS_LIST').update(value=' '.join(map(str, sudoers)))
    
    await message.reply(lang.sudoer_added)