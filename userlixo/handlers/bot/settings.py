from pyrogram import Client, filters
from pyromod.helpers import ikb
import inspect

@Client.on_callback_query(filters.sudoers & filters.regex('^settings'))
async def on_settings_cq(c, cq):
    await on_settings_u(c, cq)

@Client.on_message(filters.sudoers & filters.regex('^/settings'))
async def on_settings_txt(c, m):
    await on_settings_u(c,m)

async def on_settings_u(c, u):
    lang = u._lang
    is_query = hasattr(u, 'data')
    
    lines = [
        [(lang.language, 'setting_language')],
        [(lang.sudoers, 'setting_sudoers')],
        [(lang.env_vars, 'setting_env')]
    ]
    if is_query:
        lines.append([ (lang.back, 'start') ])
    keyb = ikb(lines)
    
    await (u.edit if is_query else u.reply)(lang.settings_text, keyb)