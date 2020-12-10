import os
import sys
from datetime import datetime
from userlixo.config import sudoers, user, bot
from userlixo.database import Config
from pyrogram import errors, Client, filters
from pyromod.helpers import ikb, array_chunk

@Client.on_callback_query(filters.sudoers & filters.regex('^setting_env'))
async def on_setting_env(c, cq):
    if cq.message:
        cq.message.chat.cancel_listener()
    lang = cq._lang
    buttons = []
    async for row in Config.all():
        btn = (f'👁‍🗨 {row.key}', f'view_env {row.key}')
        if cq.message and cq.message.from_user.id == bot.me.id:
            btn = (f'📝 {row.key}', f'edit_env {row.key}')
        buttons.append(btn)
    lines = array_chunk(buttons, 2)
    lines.append([(lang.back, 'settings')])
    keyboard = ikb(lines)
    await cq.edit(lang.settings_env_text, keyboard)

@Client.on_callback_query(filters.sudoers & filters.regex('^edit_env (?P<key>.+)'))
async def on_edit(c, cq):
    lang = cq._lang
    key = cq.matches[0]['key']
    value = (await Config.get_or_none(key=key)).value
    
    text = lang.edit_env_text(
        key=key,
        value=value
    )
    keyboard = ikb([
        [(lang.back, 'setting_env')]
    ])
    last_msg = await cq.edit(text, keyboard)
    
    env_requires_restart = ['PREFIXES', 'DATABASE_URL', 'BOT_TOKEN']
    try:
        while True:
            msg = await cq.from_user.listen(filters.text & ~filters.edited, None)
            await last_msg.remove_keyboard()
            await Config.get(key=key).update(value=msg.text)
            if key in env_requires_restart:
                text = lang.edit_env_text_restart(
                    key=key,
                    value=msg.text
                )
                keyboard = ikb([
                    [(lang.restart_now, 'restart_now')],
                    [(lang.back, 'setting_env')]
                ])
            else:
                text = lang.edit_env_text(
                    key=key,
                    value=msg.text
                )
                keyboard = ikb([
                    [(lang.back, 'setting_env')]
                ])
            last_msg = await msg.reply_text(text, reply_markup=keyboard)
    except errors.ListenerCanceled:
        pass

@Client.on_callback_query(filters.sudoers & filters.regex('^view_env (?P<key>.+)'))
async def on_view(c, cq):
    key = cq.matches[0]['key']
    value = (await Config.get_or_none(key=key)).value
    await cq.answer(value, show_alert=True)

@Client.on_callback_query(filters.sudoers & filters.regex('^restart_now'))
async def onrestart(c, cq):
    lang = cq._lang
    await cq.answer(lang.restarting_now_alert, show_alert=True)
    await cq.message.remove_keyboard()
    message_id = cq.message.message_id
    chat_id = cq.message.chat.username if cq.message.chat.username else cq.message.chat.id
    await Config.create(**{"key": "restarting_alert", "value": f'{message_id}|{chat_id}|{datetime.now().timestamp()}|restart_bot'})
    args = [sys.executable, '-m', 'userlixo']
    if '--no-update' in sys.argv:
        args.append('--no-update')
    os.execv(sys.executable, args)