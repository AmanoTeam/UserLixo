from configparser import ConfigParser
from userlixo.database import Message, Config
from pyrogram import filters, types
from pyromod.helpers import ikb, bki
import asyncio
import base64
import importlib
import json
import os
import re

def tryint(value):
    try:
        return int(value)
    except:
        return value
def b64encode(value:str):
    return base64.b64encode(value.encode()).decode()
def b64decode(value:str):
    return base64.b64decode(value.encode()).decode()

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
    try:
        answer = await self.answer(**answer_kwargs)
    except:
        pass
    edit = await self.edit_message_text(text=text, reply_markup=reply_markup, *args, **kwargs)
    return edit#, answer

def remove_keyboard(self, message_id = None, *args, **kwargs):
    return self._client.edit_message_reply_markup(self.chat.id, message_id or self.message_id, {})

async def edit_text(self, text: str, reply_markup=None, *args, **kwargs):
    if type(reply_markup) == list:
        reply_markup = ikb(reply_markup)
    return await self._client.edit_message_text(self.chat.id, self.message_id, text, reply_markup=reply_markup, **kwargs)

async def reply_text(self, text: str, reply_markup=None, *args, **kwargs):
    if reply_markup and self._client.session_name != 'bot':
        if type(reply_markup) == types.InlineKeyboardMarkup:
            reply_markup = bki(reply_markup)
        message = await Message.create(text=text, keyboard=reply_markup)
        
        bot = self._client.assistant
        inline_results = await self._client.get_inline_bot_results(bot.me.username or bot.me.id, str(message.key))
        result = inline_results.results[0]
        
        reply_to = None
        if kwargs.get('quote'):
            reply_to = self.message_id
        
        return await self._client.send_inline_bot_result(self.chat.id, inline_results.query_id, result.id, reply_to_message_id=reply_to)
    return await self.reply_text(text, reply_markup=reply_markup, *args, **kwargs)

async def get_inactive_plugins(plugins):
    inactive = (await Config.get_or_create({"value": '[]'}, key='INACTIVE_PLUGINS'))[0].value
    inactive = json.loads(inactive)
    return inactive

def reload_plugins_requirements(plugins):
    old_requirements = []
    if os.path.exists('plugins-requirements.txt'):
        with open('plugins-requirements.txt') as f:
            old_requirements = [x for x in  f.read().split('\n') if len(x)]
    requirements = []
    for plugin_type,items in plugins.items():
        for name,p in items.items():
            p_requires = p.get('requirements', '')
            p_requires = re.split('[, ]{1,}', p_requires)
            requirements.extend(p_requires)
    with open('plugins-requirements.txt', 'w') as f:
        f.write('\n'.join(requirements))
    unused = list(set(old_requirements) - set(requirements))
    return requirements, unused

def timezone_shortener(timezone):
    if timezone[-2:] == '00': # e.g. -0300 to -03
        timezone = timezone[:-2]
    if timezone[1] == '0': # e.g. -03 to -3
        timezone = timezone[0]+timezone[2:]
    if re.match('[\+-]\d+', timezone): # if timezone is not "UTC" nor ""
        timezone = 'GMT'+timezone
    return timezone

def write_plugin_info(plugins, lang, info, **kwargs):
    lang.escape_html = False
    info_lines = {"status_line": '', 'requirements_line': ''}
    for item in ['channel', 'github', 'contributors', 'type']:
        text = ''
        if item in info:
            text = getattr(lang, f'plugin_{item}_line')
            text = '\n'+text(**{item: info[item]})
        info_lines[item+'_line'] = text
    
    lang.escape_html = True
    if 'requirements' in info:
        info_lines['requirements_line'] = '\n'+lang.plugin_requirements_line(requirements=info['requirements'])
    
    text = lang.plugin_info
    text.escape_html = False
    return text(
        info=info,
        **{**info_lines, **kwargs} # make kwargs override info_lines
    )

def read_plugin_info(filename):
    with open(filename) as f:
        data = f.read()
    if not (match := re.search(r'"""\s*(?P<title>.+?)\n\n(?P<description>.+?)\n\n(?P<ini>.+?)\s*"""', data, re.DOTALL)):
        return None
    
    notation = re.sub('\.py$', '', os.path.relpath(filename)).replace('/', '.')
    basename = os.path.basename(filename)
    values = ConfigParser()
    values.read_string('[doc]\n'+match['ini'])
    values = values._sections['doc']
    
    default = dict(author='?')
    default.update(values)
    values = default
    
    plugin_type = values.get('type', 'user')
    if plugin_type not in ('user', 'bot'):
        plugin_type = 'user'
    
    info = {
        "basename": basename,
        "type": plugin_type,
        "title": match['title'],
        "description": match['description'],
        "filename": filename,
        "notation": notation,
        **values
    }
    return info

def heroku_self_deploy(heroku, app):
    api = os.getenv('HEROKU_API_KEY')
    git_url = app.git_url
    auth_url = git_url.replace('://', f'://api:{api}@')
    
    if os.path.exists('.gitignore'):
        os.remove('.gitignore')
    
    os.system(f'''\
        git config --global user.name "UserLixo"; \
        git config --global user.email "user@lixo.com"; \
        git remote add app {auth_url}; \
        git remote set-url app {auth_url}; \
        \
        git fetch app && \
        git add . && \
        git commit -m "Upgrade UserLixo" && \
        git push -f app master
    ''')