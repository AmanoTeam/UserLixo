from userlixo.config import plugins, user, bot
from userlixo.database import Config
from userlixo.handlers.bot.list_plugins import on_list_plugins_type
from pyrogram import Client, filters
from pyromod.helpers import ikb
from userlixo.utils import get_inactive_plugins, write_plugin_info
import importlib
import json
import os
import re

@Client.on_callback_query(filters.sudoers & filters.regex('^info_plugin (?P<basename>.+) (?P<plugin_type>user|bot) (?P<pg>\d+)'))
async def on_info_plugin(c,cq):
    lang = cq._lang
    basename = cq.matches[0]['basename']
    plugin_type = cq.matches[0]['plugin_type']
    pg = int(cq.matches[0]['pg'])
    
    if basename not in plugins[plugin_type]:
        return await cq.answer('UNKNOWN')
    
    plugin = plugins[plugin_type][basename]
    
    status = lang.active
    first_btn = (lang.deactivate, f'deactivate_plugin {basename} {plugin_type} {pg}')
    
    inactive = await get_inactive_plugins(plugins)

    if plugin['notation'] in inactive:
        status = lang.inactive
        first_btn = (lang.activate, f'activate_plugin {basename} {plugin_type} {pg}')
    status_line = '\n'+status
    
    lines = [
        [first_btn, (lang.remove, f'remove_plugin {basename} {plugin_type} {pg}')]
    ]
    if 'settings' in plugin and plugin['settings']:
        lines.append( [(lang.settings, f'plugin_settings {basename} {plugin_type} {pg}')] )
    lines.append( [(lang.back, f'{plugin_type}_plugins {pg}')] )
    keyb = ikb(lines)
    
    text = write_plugin_info(plugins, lang, plugin, status_line=status_line)
    await cq.edit(text, keyb, disable_web_page_preview=True)

@Client.on_callback_query(filters.sudoers & filters.regex('^(?P<deactivate>de)?activate_plugin (?P<basename>.+) (?P<plugin_type>user|bot) (?P<pg>\d+)'))
async def on_switch_plugin(c,cq):
    lang = cq._lang
    basename = cq.matches[0]['basename']
    plugin_type = cq.matches[0]['plugin_type']
    deactivate = cq.matches[0]['deactivate']
    if basename not in plugins[plugin_type]:
        return await cq.answer(lang.plugin_not_found(name=plugin))
    
    plugin = plugins[plugin_type][basename]
    
    if not os.path.exists(plugin['filename']):
        return await cq.edit(lang.plugin_not_exists_on_server)
    
    inactive = await get_inactive_plugins(plugins)
    
    if deactivate:
        inactive.append(plugin['notation'])
    else:
        inactive = [x for x in inactive if x != plugin['notation']]
    
    inactive = [*set(inactive)] # make values unique
    await Config.get(key='INACTIVE_PLUGINS').update(value=json.dumps(inactive))
    
    try:
        module = importlib.import_module(plugin['notation'])
    except Exception as e:
        os.remove(plugin['filename'])
        return await cq.edit(lang.plugin_could_not_load(e=e))
    
    functions = [*filter(callable, module.__dict__.values())]
    functions = [*filter(lambda f: hasattr(f, 'handler'), functions)]
    
    client = (user,bot)[plugin_type=='bot']
    for f in functions:
        (client.remove_handler if deactivate else client.add_handler)(*f.handler)
    
    text = lang.plugin_has_been_deactivated if deactivate else lang.plugin_has_been_activated
    await cq.answer(text)
    await on_info_plugin(c,cq)

@Client.on_callback_query(filters.sudoers & filters.regex('^remove_plugin (?P<basename>.+) (?P<plugin_type>user|bot) (?P<page>\d+)'))
async def on_remove_plugin(c,cq):
    lang = cq._lang
    basename = cq.matches[0]['basename']
    plugin_type = cq.matches[0]['plugin_type']
    pg = cq.matches[0]['page']
    
    if basename not in plugins[plugin_type]:
        return await cq.answer(lang.plugin_not_found(name=basename))
    
    plugin = plugins[plugin_type][basename]
    
    inactive = await get_inactive_plugins(plugins)
    
    if not os.path.exists(plugin['filename']):
        return await cq.edit(lang.plugin_not_exists_on_server)
    
    if plugin['notation'] in inactive:
        inactive = [x for x in inactive if x != plugin['notation']]
        await Config.get(key='INACTIVE_PLUGINS').update(value=json.dumps(inactive))
    
    try:
        module = importlib.import_module(plugin['notation'])
    except Exception as e:
        os.remove(plugin['filename'])
        return await cq.edit(lang.plugin_could_not_load(e=e))
    
    functions = [*filter(callable, module.__dict__.values())]
    functions = [*filter(lambda f: hasattr(f, 'handler'), functions)]
    
    client = (user,bot)[plugin_type=='bot']
    for f in functions:
        client.remove_handler(*f.handler)
    del plugins[plugin_type][basename]
    os.remove(plugin['filename'])
    
    await cq.answer(lang.plugin_removed(name=basename))
    cq.matches = [{"page": pg, "type": plugin_type}]
    await on_list_plugins_type(c,cq)