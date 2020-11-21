from bot_handlers.callback_query.plugins import onplugins
from bot_handlers.message.add_plugin import onaddplugin_txt
from config import plugins, client
from database import Config
from pyrogram import Client, filters
import hashlib
import importlib
import json
import os
import re

@Client.on_message(filters.su_cmd('plugins$'))
async def onplugins_txt(c,m):
    m.matches = [{"page": 0}]

@Client.on_message(filters.reply & filters.su_cmd('(plugin )?(?P<action>add|rm|\+|-)'))
async def on_plugin_action(c, m):
    lang = m.lang
    action = m.matches[0]['action']
    if action in ['+', 'add']:
        await m.delete()
        return await onaddplugin_txt(c,m)
    
    # remove plugin on .plugin rm
    act = m.edit if await filters.me(c,m) else m.reply
    msg = m.reply_to_message
    
    if not msg.document:
        return await act(lang.plugin_rm_not_document)
    if not msg.document.file_name.endswith('.py'):
        return await act(lang.plugin_rm_not_py)
    
    plugin = os.path.basename(msg.document.file_name)
    
    if plugin not in plugins:
        return await act(lang.plugin_rm_not_added(name=plugin))
    
    info = plugins[plugin]
    
    # compare files via hash
    temp_filename = await msg.download()
    with open(temp_filename) as temp_file, open(info['filename']) as local_file:
        local_data = local_file.read()
        local_hash = hashlib.md5(local_data.encode()).hexdigest()[:10]
        temp_data = temp_file.read()
        remote_hash = hashlib.md5(temp_data.encode()).hexdigest()[:10]
    os.remove(temp_filename)
    if local_hash != remote_hash:
        return await act(lang.plugin_rm_remote_local_are_diff(name=plugin))
    
    plugin_notation = re.search('handlers\.(.+)', info['notation'])[1]
    inactive = (await Config.get_or_create({"value": '[]'}, key='INACTIVE_PLUGINS'))[0].value
    inactive = json.loads(inactive)
    
    if not os.path.exists(info['filename']):
        del plugins[plugin]
        return await act(lang.plugin_not_exists_on_server)
    
    if plugin_notation in inactive:
        inactive = [x for x in inactive if x != plugin_notation]
        await Config.get(key='INACTIVE_PLUGINS').update(value=json.dumps(inactive))
    
    try:
        module = importlib.import_module(info['notation'])
    except Exception as e:
        os.remove(info['filename'])
        return await act(lang.plugin_could_not_load(e=e))
    
    functions = [*filter(callable, module.__dict__.values())]
    functions = [*filter(lambda f: hasattr(f, 'handler'), functions)]
    
    for f in functions:
        client.remove_handler(*f.handler)
    del plugins[plugin]
    os.remove(info['filename'])
    
    await act(lang.plugin_removed_text(name=plugin))