from userlixo.config import sudoers, user, bot
from userlixo.database import Config
from userlixo.utils import tryint
from pyrogram import Client, filters
from pyromod.helpers import ikb, array_chunk

async def sudoers_interface(cq):
    lang = cq._lang
    c = cq._client
    text = lang.setting_sudoers_text+"\n"
    buttons = []
    added = []
    for user_id in sudoers:
        try:
            user_obj = await c.get_users(user_id)
        except:
            import traceback; traceback.print_exc()
            user_obj = None
        id = user_obj.id if user_obj else user_id
        if id in added:
            continue
        added.append(id)
        
        mention = user_id
        if user_obj:
            mention = f'@{user_obj.username}' if user_obj.username else user_obj.first_name
        text += f"\n👤 {mention}"
        
        if id not in ['me', user.me.id, cq.from_user.id]:
            buttons.append((f"🗑 {mention}", f'remove_sudoer {user_id}'))
        
    lines = array_chunk(buttons, 2)
    if bot.me.username:
        lines.append([(lang.add_sudoer, f"https://t.me/{bot.me.username}?start=add_sudoer", 'url')])
    lines.append([(lang.back, 'settings')])
    keyboard = ikb(lines)
    return text, keyboard

@Client.on_callback_query(filters.sudoers & filters.regex('^setting_sudoers'))
async def on_setting_sudoers(c, cq):
    lang = cq._lang
    text, keyboard = await sudoers_interface(cq)
    await cq.edit(text, keyboard)

@Client.on_callback_query(filters.sudoers & filters.regex('^remove_sudoer (?P<who>\w+)'))
async def on_remove_sudoer(c, cq):
    lang = cq._lang
    who = tryint(cq.matches[0]['who'])
    
    # Sanitize list
    sudoers[:] = [*map(tryint, sudoers)]
    removed = [x for x in sudoers if x != who]
    sudoers[:] = removed
    
    await Config.get(key='SUDOERS_LIST').update(
        value=' '.join( [*map(str, sudoers)] )
    )
    
    text, keyboard = await sudoers_interface(cq)
    await cq.edit(text, keyboard)