from config import sudoers
from database import Config
from pyrogram import Client, Filters
from pyromod.helpers import ikb, array_chunk
from utils import info

async def sudoers_interface(query):
    lang = query.lang
    client = query._client
    text = lang.setting_sudoers_text+"\n"
    buttons = []
    added = []
    for user in sudoers:
        try:
            user_obj = await client.get_users(user)
        except:
            import traceback; traceback.print_exc()
            user_obj = None
        id = user_obj.id if user_obj else user
        if id in added:
            continue
        added.append(id)
        
        mention = user
        if user_obj:
            mention = f'@{user_obj.username}' if user_obj.username else user_obj.first_name
        text += f"\n👤 {mention}"
        
        if id not in [info['user'].id, query.from_user.id]:
            buttons.append((f"🗑 {mention}", f'remove_sudoer {user}'))
        
    lines = array_chunk(buttons, 2)
    if info['bot'].username:
        lines.append([(lang.add_sudoer, f"https://t.me/{info['bot'].username}?start=add_sudoer", 'url')])
    lines.append([(lang.back, 'settings')])
    keyboard = ikb(lines)
    return text, keyboard

@Client.on_callback_query(Filters.su_regex('^setting_sudoers'))
async def on_setting_language(client, query):
    lang = query.lang
    text, keyboard = await sudoers_interface(query)
    await query.edit(text, keyboard)

@Client.on_callback_query(Filters.su_regex('^remove_sudoer (?P<who>\w+)'))
async def on_remove_sudoer(client, query):
    lang = query.lang
    who = query.matches[0]['who']
    sudoers[:] = [*map(str, filter(lambda x: x != who, sudoers))]
    await Config.get(key='SUDOERS_LIST').update(value=' '.join(sudoers))
    
    text, keyboard = await sudoers_interface(query)
    await query.edit(text, keyboard)