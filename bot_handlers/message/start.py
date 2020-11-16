from pyrogram import Client, filters
from pyromod.helpers import ikb
from utils import shell_exec
import os, re, sys
from database import Config
from datetime import datetime

@Client.on_message(filters.sudoers & filters.regex('^/start add_plugin$'))
async def onaddplugin(c, m):
    await m.reply('Plugins support are under development.')

@Client.on_message(filters.sudoers & filters.regex('^/start'))
async def onstart(c, m):
    lang = m.lang
    keyb = ikb([
        [(lang.upgrade, 'upgrade'), [lang.restart, 'restart']],
        [(lang.commands, 'list_commands 0 start'), (lang.plugins, 'list_plugins 0 start')],
        [(lang.help, 'help start'), (lang.settings, 'settings start')]
    ])
    text = lang.start_text
    await m.reply(text, keyb)

@Client.on_callback_query(filters.sudoers & filters.regex('^start'))
async def onstartcb(c, cq):
    lang = cq.lang
    m = cq.message
    keyb = ikb([
        [(lang.upgrade, 'upgrade'), [lang.restart, 'restart']],
        [(lang.commands, 'list_commands 0 start'), (lang.plugins, 'list_plugins 0 start')],
        [(lang.help, 'help start'), (lang.settings, 'settings start')]
    ])
    text = lang.start_text
    await cq.edit(text, keyb)