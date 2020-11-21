from config import plugins, client
from configparser import ConfigParser
from database import Config
from pyrogram import Client, filters
from pyromod.helpers import ikb
import importlib
import json
import math
import os
import re

@Client.on_message(filters.sudoers & filters.document)
async def on_plugin_file(c, m):
    if m.document.file_name.endswith('.py'):
        await onaddplugin_txt(c,m)

@Client.on_message(filters.sudoers & filters.regex('^/(start )?plugin[_ ]add'))
async def onaddplugin_txt(c, m):
    if hasattr(m, 'data'):
        await m.message.delete()
    lang = m.lang
    loop_time = 0
    while True:
        loop_time += 1
        if m.document:
            msg = m
            if loop_time > 1:
                break # avoid infinite loop
        elif m.reply_to_message and m.reply_to_message.document:
            msg = m.reply_to_message
            if loop_time > 1:
                break # avoid infinite loop
        else:
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
    filename = await msg.download(f'cache/')
    filename = os.path.relpath(filename)
    
    with open(filename) as f:
        data = f.read()
    if not (match := re.search(r'"""\s*(?P<title>.+)\n\n(?P<description>.+)\n\n(?P<ini>.+)\s*"""', data, re.DOTALL)):
        os.remove(filename)
        return await m.reply(lang.plugin_info_block_not_found, quote=True)
    
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
    
    status_line = ''
    text = lang.plugin_info
    text.escape_html = False
    text = text(
        info=info,
        status_line=status_line,
        channel_line=channel_line,
        github_line=github_line,
        requirements_line=requirements_line,
        contributors_line=contributors_line
    )
    kb = [
        [(lang.add, f'confirm_add_plugin {filename}'), (lang.cancel, 'cancel_plugin')]
    ]
    if c.bot_token: # if is bot
        kb = ikb(kb)
    await msg.reply(text, kb, disable_web_page_preview=True, quote=True)

@Client.on_callback_query(filters.sudoers & filters.regex('^cancel_plugin'))
async def oncancelplugin(c, cq):
    lang = cq.lang
    await cq.edit(lang.command_canceled)

@Client.on_callback_query(filters.sudoers & filters.regex('^confirm_add_plugin (?P<filename>.+)'))
async def on_confirm_plugin(c, cq):
    lang = cq.lang
    module = None
    
    cache_filename = cq.matches[0]['filename']
    basename = os.path.basename(cache_filename)
    new_filename = 'handlers/plugins/'+basename
    notation = re.sub('\.py$', '', new_filename).replace('/', '.')
    
    # Safely unload the plugin if existent
    if os.path.exists(new_filename):
        try:
            module = importlib.import_module(notation)
        except Exception as e:
            return await cq.edit(lang.plugin_could_not_load_existent(e=e))
        
        functions = [*filter(callable, module.__dict__.values())]
        functions = [*filter(lambda f: hasattr(f, 'handler'), functions)]
        for f in functions:
            client.remove_handler(*f.handler)
    
    os.rename(cache_filename, new_filename)
    
    with open(new_filename) as f:
        data = f.read()
    match = re.search(r'"""\s*(?P<title>.+)\n\n(?P<description>.+)\n\n(?P<ini>.+)\s*"""', data, re.DOTALL)
    
    values = ConfigParser()
    values.read_string('[doc]\n'+match['ini'])
    values = values._sections['doc']
    
    try:
        if module:
            importlib.reload(module)
        module = importlib.import_module(notation)
    except Exception as e:
        os.remove(new_filename)
        return await cq.edit(lang.plugin_could_not_load(e=e))
    
    functions = [*filter(callable, module.__dict__.values())]
    functions = [*filter(lambda f: hasattr(f, 'handler'), functions)]
    
    if not len(functions):
        os.remove(new_filename)
        return await cq.edit(lang.plugin_has_no_handlers)
    
    for f in functions:
        client.add_handler(*f.handler)
    
    plugins[basename] = dict(title=match['title'], description=match['description'], filename=new_filename, notation=notation, **values)
    
    inactive = (await Config.get_or_create({"value": '[]'}, key='INACTIVE_PLUGINS'))[0].value
    inactive = json.loads(inactive)
    plugin_notation = re.search('handlers\.(.+)', notation)[1]

    if plugin_notation in inactive:
        inactive = [x for x in inactive if x != plugin_notation]
        await Config.get(key='INACTIVE_PLUGINS').update(value=json.dumps(inactive))

    # Discover which page is this plugin listed in
    quant_per_page = 4*2 # lines times columns
    page = math.ceil(len(plugins)/quant_per_page)
    
    keyb = ikb([
        [(lang.see_plugin_info, f'info_plugin {basename} {page}')]
    ])
    await cq.edit(lang.plugin_added(name=basename), keyb)