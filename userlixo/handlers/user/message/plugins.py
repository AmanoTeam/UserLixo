from userlixo.config import plugins, user, bot
from userlixo.database import Config
from userlixo.handlers.bot.add_plugin import on_add_plugin_u
from userlixo.handlers.bot.list_plugins import on_list_plugins_u
from pyrogram import Client, filters
from userlixo.utils import read_plugin_info
import hashlib
import importlib
import json
import os
import re

@Client.on_message(filters.sudoers & filters.document & filters.private & ~filters.me)
async def on_plugin_file(c, m):
    if m.document.file_name.endswith('.py'):
        await on_add_plugin_u(c,m)

@Client.on_message(filters.su_cmd('plugins$'))
async def on_list_plugins_txt(c,m):
    await on_list_plugins_u(c,m)

@Client.on_message(filters.reply & filters.su_cmd('(plugin )?(?P<action>add|rm|\+|-)'))
async def on_plugin_action(c, m):
    lang = m._lang
    action = m.matches[0]['action']
    if action in ['+', 'add']:
        if await filters.me(c,m):
            await m.delete()
        return await on_add_plugin_u(c,m)
    
    # remove plugin on .plugin rm
    act = m.edit if await filters.me(c,m) else m.reply
    msg = m.reply_to_message
    
    if not msg.document:
        return await act(lang.plugin_rm_not_document)
    if not msg.document.file_name.endswith('.py'):
        return await act(lang.plugin_rm_not_py)
    
    basename = msg.document.file_name
    cache_filename = await msg.download('cache/')
    plugin = read_plugin_info(cache_filename)
    if not plugin:
        os.remove(cache_filename)
        return await msg.reply(lang.plugin_info_block_not_found, quote=True)
    plugin_type = plugin['type']
    
    if basename not in plugins[plugin_type]:
        return await act(lang.plugin_rm_not_added(name=basename))
    
    plugin = plugins[plugin_type][basename]
    
    # compare files via hash
    with open(cache_filename) as remote_file, open(plugin['filename']) as local_file:
        local_data = local_file.read()
        local_hash = hashlib.md5(local_data.encode()).hexdigest()[:10]
        
        temp_data = remote_file.read()
        remote_hash = hashlib.md5(temp_data.encode()).hexdigest()[:10]
    os.remove(cache_filename)
    
    if local_hash != remote_hash:
        return await act(lang.plugin_rm_remote_local_are_diff(name=basename))
    
    inactive = await get_inactive_plugins(plugins)
    
    if not os.path.exists(plugin['filename']):
        del plugins[plugin_type][basename]
        return await act(lang.plugin_not_exists_on_server)
    
    if plugin['notation'] in inactive:
        inactive = [x for x in inactive if x != plugin['notation']]
        await Config.get(key='INACTIVE_PLUGINS').update(value=json.dumps(inactive))
    
    try:
        module = importlib.import_module(plugin['notation'])
    except Exception as e:
        os.remove(plugin['filename'])
        return await act(lang.plugin_could_not_load(e=e))
    
    functions = [*filter(callable, module.__dict__.values())]
    functions = [*filter(lambda f: hasattr(f, 'handler'), functions)]
    
    client = (user, bot)[plugin_type=='bot']
    for f in functions:
        client.remove_handler(*f.handler)
    del plugins[plugin_type][basename]
    os.remove(plugin['filename'])
    
    await act(lang.plugin_removed_text(name=basename))