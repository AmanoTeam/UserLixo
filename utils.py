from database import Message, Config
from pyrogram import filters
from pyromod.helpers import ikb
import asyncio
import json
import re

info = {"user": {}, "bot": {}}

def tryint(value):
    try:
        return int(value)
    except:
        return value

async def shell_exec(code, treat=True):
    process = await asyncio.create_subprocess_shell(code,
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.STDOUT)
    
    stdout = (await process.communicate())[0]
    if treat:
        stdout = stdout.decode().strip()
    return stdout, process

# Pyrogram monkeypatch
async def query_edit(self, text, reply_markup=None, answer_kwargs={}, *args, **kwargs):
    answer = await self.answer(**answer_kwargs)
    edit = await self.edit_message_text(text=text, reply_markup=reply_markup, *args, **kwargs)
    return edit#, answer

def remove_keyboard(self, message_id = None, *args, **kwargs):
    return self._client.edit_message_reply_markup(self.chat.id, message_id or self.message_id, {})

async def edit_text(self, text: str, reply_markup=None, *args, **kwargs):
    if type(reply_markup) == list:
        reply_markup = ikb(reply_markup)
    return await self._client.edit_message_text(self.chat.id, self.message_id, text, reply_markup=reply_markup, **kwargs)

async def reply_text(self, text: str, reply_markup=None, *args, **kwargs):
    if reply_markup and not self._client.bot_token:
        message = await Message.create(text=text, keyboard=reply_markup)
        
        inline_results = await self._client.get_inline_bot_results(info['bot'].username or info['bot'].id, str(message.key))
        result = inline_results.results[0]
        
        reply_to = None
        if kwargs.get('quote'):
            reply_to = self.message_id
        
        return await self._client.send_inline_bot_result(self.chat.id, inline_results.query_id, result.id, reply_to_message_id=reply_to)
    return await self.reply_text(text, reply_markup=reply_markup, *args, **kwargs)

async def get_inactive_names(plugins):
    inactive = (await Config.get_or_create({"value": '[]'}, key='INACTIVE_PLUGINS'))[0].value
    inactive = json.loads(inactive)
    result = []
    for name,info in plugins.items():
        plugin_notation = re.search('handlers\.(.+)', info['notation'])[1]
        if plugin_notation in inactive:
            result.append(name)
    return result