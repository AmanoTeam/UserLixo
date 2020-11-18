from config import plugins, client
from database import Config
from pyrogram import Client, filters
from pyromod.helpers import ikb
from pyromod.nav import Pagination
from utils import info, get_inactive_names
import importlib
import json
import os
import re

@Client.on_callback_query(filters.sudoers & filters.regex('^list_plugins (?P<page>\d+)'))
async def onplugins(c,cq):
    # Determining type of update
    query = hasattr(cq, 'data') 
    
    lang = cq.lang
    this_page = int(cq.matches[0]['page'] or 0)
    
    item_format = 'info_plugin {} {}'
    page_format = 'list_plugins {}'
    if query and cq.data.endswith('start'):
        item_format = 'info_plugin {} {} start'
        page_format = 'list_plugins {} start'
    
    inactive_names = await get_inactive_names(plugins)
    def item_title(i, pg):
        name = i[0]
        status = '💤' if name in inactive_names else '❇️'
        return f'{status} {name}'
    page = Pagination(
        [*plugins.items()],
        item_data=lambda i, pg: item_format.format(i[0], pg),
        item_title=item_title,
        page_data=lambda pg: page_format.format(pg)
    )
    
    lines = page.create(this_page, lines=4, columns=2)
    total = len(lines)
    
    if hasattr(cq, 'from_bot_handler') or (hasattr(cq, 'message') and cq.message):
        lines.append([(lang.add_plugin, f'add_plugin {this_page} start')])
    else:
        lines.append([(lang.add_plugin, f"t.me/{info['bot']['username']}?start=add_plugin", 'url')])
    
    if query and cq.data.endswith('start'):
        lines.append([(lang.back, 'start')])
    elif query:
        lines.append([(lang.back, 'help')])
    if query:
        return await cq.edit(lang.plugins_text, ikb(lines))
    if hasattr(cq, 'from_bot_handler'):
        lines = ikb(lines)
    await cq.reply(lang.plugins_text, lines)

@Client.on_callback_query(filters.sudoers & filters.regex('^info_plugin (?P<plugin>.+) (?P<pg>\d+)'))
async def onshowplugin(c,cq):
    lang = cq.lang
    plugin = cq.matches[0]['plugin']
    pg = int(cq.matches[0]['pg'])
    
    if plugin not in plugins:
        return await cq.answer('UNKNOWN')
    
    info = plugins[plugin]
    
    back_data = f'list_plugins {pg}'
    append_data = ''
    if cq.data.endswith('start'):
        append_data = ' start'
    
    plugin_notation = re.search('handlers\.(.+)', info['notation'])[1]
    status = lang.active
    first_btn = (lang.deactivate, f'deactivate_plugin {plugin} {pg}'+append_data)
    
    inactive = (await Config.get_or_create({"value": '[]'}, key='INACTIVE_PLUGINS'))[0].value
    inactive = json.loads(inactive)

    if plugin_notation in inactive:
        status = lang.inactive
        first_btn = (lang.activate, f'activate_plugin {plugin} {pg}'+append_data)
    status_line = '\n'+status
    kb = ikb([
        [first_btn, (lang.remove, f'remove_plugin {plugin} {pg}'+append_data)],
        [(lang.back, back_data+append_data)]
    ])
    
    info_text = []
    for k,v in info.items():
        info_text.append(f'<b>{k}</b>: {v}')
    info_text = '\n'.join(info_text)
    
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
    await cq.edit(text, kb, disable_web_page_preview=True)

@Client.on_callback_query(filters.sudoers & filters.regex('^deactivate_plugin (?P<plugin>.+) (?P<pg>\d+)'))
async def ondeactivatelugin(c,cq):
    lang = cq.lang
    plugin = cq.matches[0]['plugin']
    
    if plugin not in plugins:
        return await cq.answer('UNKNOWN')
    
    info = plugins[plugin]
    
    plugin_notation = re.search('handlers\.(.+)', info['notation'])[1]
    inactive = (await Config.get_or_create({"value": '[]'}, key='INACTIVE_PLUGINS'))[0].value
    inactive = json.loads(inactive)
    
    if not os.path.exists(info['filename']):
        return await cq.edit(lang.plugin_not_exists_on_server)
    
    if plugin_notation not in inactive:
        inactive.append(plugin_notation)
        await Config.get(key='INACTIVE_PLUGINS').update(value=json.dumps(inactive))
    
    try:
        module = importlib.import_module(info['notation'])
    except Exception as e:
        os.remove(info['filename'])
        return await cq.edit(lang.plugin_could_not_load(e=e))
    
    functions = [*filter(callable, module.__dict__.values())]
    functions = [*filter(lambda f: hasattr(f, 'handler'), functions)]
    
    for f in functions:
        client.remove_handler(*f.handler)
    await cq.answer(lang.plugin_has_been_deactivated)
    await onshowplugin(c,cq)

@Client.on_callback_query(filters.sudoers & filters.regex('^activate_plugin (?P<plugin>.+) (?P<pg>\d+)'))
async def onactivatelugin(c,cq):
    lang = cq.lang
    plugin = cq.matches[0]['plugin']
    
    if plugin not in plugins:
        return await cq.answer('UNKNOWN')
    
    info = plugins[plugin]
    
    plugin_notation = re.search('handlers\.(.+)', info['notation'])[1]
    inactive = (await Config.get_or_create({"value": '[]'}, key='INACTIVE_PLUGINS'))[0].value
    inactive = json.loads(inactive)
    
    if not os.path.exists(info['filename']):
        return await cq.edit(lang.plugin_not_exists_on_server)
    
    if plugin_notation in inactive:
        inactive = [x for x in inactive if x != plugin_notation]
        await Config.get(key='INACTIVE_PLUGINS').update(value=json.dumps(inactive))
    
    try:
        module = importlib.import_module(info['notation'])
    except Exception as e:
        os.remove(info['filename'])
        return await cq.edit(lang.plugin_could_not_load(e=e))
    
    functions = [*filter(callable, module.__dict__.values())]
    functions = [*filter(lambda f: hasattr(f, 'handler'), functions)]
    
    for f in functions:
        client.add_handler(*f.handler)
    
    await cq.answer(lang.plugin_has_been_activated)
    await onshowplugin(c,cq)

@Client.on_callback_query(filters.sudoers & filters.regex('^remove_plugin (?P<plugin>.+) (?P<page>\d+)'))
async def onremoveplugin(c,cq):
    lang = cq.lang
    plugin = cq.matches[0]['plugin']
    pg = cq.matches[0]['page']
    
    if plugin not in plugins:
        return await cq.answer('UNKNOWN')
    
    info = plugins[plugin]
    
    plugin_notation = re.search('handlers\.(.+)', info['notation'])[1]
    inactive = (await Config.get_or_create({"value": '[]'}, key='INACTIVE_PLUGINS'))[0].value
    inactive = json.loads(inactive)
    
    if not os.path.exists(info['filename']):
        return await cq.edit(lang.plugin_not_exists_on_server)
    
    if plugin_notation in inactive:
        inactive = [x for x in inactive if x != plugin_notation]
        await Config.get(key='INACTIVE_PLUGINS').update(value=json.dumps(inactive))
    
    try:
        module = importlib.import_module(info['notation'])
    except Exception as e:
        os.remove(info['filename'])
        return await cq.edit(lang.plugin_could_not_load(e=e))
    
    functions = [*filter(callable, module.__dict__.values())]
    functions = [*filter(lambda f: hasattr(f, 'handler'), functions)]
    
    for f in functions:
        client.remove_handler(*f.handler)
    del plugins[plugin]
    os.remove(info['filename'])
    
    cq.data = f'list_plugins {pg}'
    if cq.data.endswith('start'):
        cq.data += ' start'
    await cq.answer(lang.plugin_removed(name=plugin))
    await onplugins(c,cq)