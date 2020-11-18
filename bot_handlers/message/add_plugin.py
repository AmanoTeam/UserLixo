from config import plugins, client
from configparser import ConfigParser
from pyrogram import Client, filters
from pyromod.helpers import ikb
import importlib
import hashlib
import math
import os
import re

@Client.on_message(filters.sudoers & filters.regex('^/start add_plugin$'))
async def onaddplugin_txt(c, m):
    if hasattr(m, 'data'):
        await m.message.delete()
    lang = m.lang
    while True:
        msg = await m.from_user.ask(lang.plugin_file_ask)
        if await filters.regex('/cancel')(c,msg):
            return await msg.reply(lang.command_canceled)
        if not msg.document:
            await msg.reply(lang.plugin_waiting_file, quote=True)
            continue
        if not re.search('(py)$', msg.document.file_name):
            await msg.reply(lang.plugin_format_not_accepted, quote=True)
            continue
        if msg.document.file_size > (5*1024*1024):
            await msg.reply(lang.plugin_too_big, quote=True)
            continue
        break
    filename = await msg.download('handlers/plugins/')
    filename = os.path.relpath(filename)
    
    with open(filename) as f:
        data = f.read()
    if not (match := re.search(r'"""\s*(?P<title>.+)\n\n(?P<description>.+)\n\n(?P<ini>.+)\s*"""', data, re.DOTALL)):
        os.remove(filename)
        return await m.reply(lang.plugin_info_block_not_found, quote=True)
    
    os.remove(filename)
    status = 'Active'
    basename = os.path.basename(filename)
    values = ConfigParser()
    values.read_string('[doc]\n'+match['ini'])
    values = values._sections['doc']
    info = dict(title=match['title'], description=match['description'], filename=filename, **values)
    
    # Showing info
    channel_line = github_line = requirements_line = contributors_line = ''
    lang.escape_html = False
    if 'channel' in info:
        channel_line = '\n'+lang.plugin_channel_line(channel=info['channel'])
    if 'github' in info:
        github_line = '\n'+lang.plugin_github_line(github=info['github'])
    if 'contributors' in info:
        contributors_line = '\n'+lang.plugin_contributors_line(contributors=info['contributors'])
    lang.escape_html = True
    if 'requirements' in info:
        requirements_line = '\n'+lang.plugin_requirements_line(requirements=info['requirements'])
    
    status = 'Active'
    text = lang.plugin_info
    text.escape_html = False
    text = text(
        info=info,
        status=status,
        channel_line=channel_line,
        github_line=github_line,
        requirements_line=requirements_line,
        contributors_line=contributors_line
    )
    file_hash = hashlib.md5(msg.document.file_id.encode()).hexdigest()[:10]
    kb = ikb([
        [(lang.add, f'confirm_add_plugin {file_hash}'), (lang.cancel, 'cancel_plugin')]
    ])
    await msg.reply(text, kb, disable_web_page_preview=True, quote=True)

@Client.on_callback_query(filters.sudoers & filters.regex('^cancel_plugin'))
async def oncancelplugin(c, cq):
    lang = cq.lang
    await cq.edit(lang.command_canceled)

@Client.on_callback_query(filters.sudoers & filters.regex('^confirm_add_plugin (?P<file_hash>.+)'))
async def on_confirm_plugin(c, cq):
    lang = cq.lang
    if not (msg := cq.message.reply_to_message):
        await cq.message.remove_keyboard()
        return await cq.answer('FILE NOT FOUND', show_alert=True)
        
    expected_hash = cq.matches[0]['file_hash']
    now_hash = hashlib.md5(msg.document.file_id.encode()).hexdigest()[:10]
    if now_hash != expected_hash:
        await cq.message.remove_keyboard()
        return await cq.answer('FILE HAS CHANGED', show_alert=True)
    
    filename = await msg.download('handlers/plugins/')
    filename = os.path.relpath(filename)
    basename = os.path.basename(filename)
    
    with open(filename) as f:
        data = f.read()
    match = re.search(r'"""\s*(?P<title>.+)\n\n(?P<description>.+)\n\n(?P<ini>.+)\s*"""', data, re.DOTALL)
    
    values = ConfigParser()
    values.read_string('[doc]\n'+match['ini'])
    values = values._sections['doc']
    
    namespace = re.sub('\.py$', '', filename).replace('/', '.')
    try:
        module = importlib.import_module(namespace)
    except Exception as e:
        os.remove(filename)
        return await cq.edit(lang.plugin_could_not_load(e=e))
    
    functions = [*filter(callable, module.__dict__.values())]
    functions = [*filter(lambda f: hasattr(f, 'handler'), functions)]
    
    if not len(functions):
        os.remove(filename)
        return await cq.edit(lang.plugin_has_no_handlers)
    
    for f in functions:
        client.add_handler(*f.handler)
        
    plugins[basename] = dict(title=match['title'], description=match['description'], filename=filename, **values)
    # Discover which page is this plugin listed in
    quant_per_page = 4*2 # lines times columns
    page = math.ceil(len(plugins)/quant_per_page)
    
    keyb = ikb([
        [(lang.see_plugin_info, f'info_plugin {basename} {page}')]
    ])
    await cq.edit(lang.plugin_added(name=basename), keyb)