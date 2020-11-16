import asyncio
import base64
import glob
import json
import re
import os
import pyrogram
import yaml

from database import Config
from dotenv import load_dotenv
from langs import Langs

from pyromod import listen, filters
from pyrogram import Client, filters
from utils import tryint, query_edit, remove_keyboard, reply_text, edit_text

# Load variables on .env to os.environ
if not os.getenv('DYNO'):
    if not os.path.exists('.env'):
        raise Exception('File .env is missing')
    load_dotenv('.env')

def b64encode(value:str):
    return base64.b64encode(value.encode()).decode()
def b64decode(value:str):
    return base64.b64decode(value.encode()).decode()

required_env_vars = ['DATABASE_URL', 'BOT_TOKEN']
for required in required_env_vars:
    if required not in os.environ:
        raise AttributeError(f'Missing required env variable: {required}')
    if not os.getenv(required):
        raise ValueError(f'Invalid value for required env variable {required}')

sudoers = []
environment_vars = ['DATABASE_URL', 'LOGS_CHAT', 'SUDOERS_LIST', 'LANGUAGE', 'BOT_TOKEN', 'PREFIXES']

async def load_env():
    if not os.getenv('LOGS_CHAT'):
        os.environ['LOGS_CHAT'] = 'me'
    if not os.getenv('LANGUAGE'):
        os.environ['LANGUAGE'] = 'en'
    if not os.getenv('PREFIXES'):
        os.environ['PREFIXES'] = '.'
    
    for env_key in environment_vars:
        os.environ[env_key] = (await Config.get_or_create({"value": os.getenv(env_key, '')}, key=env_key))[0].value
    
    langs.code = os.environ['LANGUAGE']
    
    sudoers.extend(
        [*map(lambda s: s.lstrip('@').lower() if type(s) == str else s, os.getenv('SUDOERS_LIST').split())]
    )

# Extra **kwargs for creating pyrogram.Client
pyrogram_config = os.getenv('PYROGRAM_CONFIG') or b64encode('{}')
pyrogram_config = b64decode(pyrogram_config)
pyrogram_config = json.loads(pyrogram_config)

# All monkeypatch stuff must be done before the Client instance is created
def filter_sudoers(flt, client, update):
    if not update.from_user:
        return
    user = update.from_user
    return user.id in sudoers or (user.username and user.username.lower() in sudoers)
def filter_su_cmd(command, prefixes=None, *args, **kwargs):
    prefixes = ''.join(prefixes) if type(prefixes) == list else prefixes or os.getenv('PREFIXES') or '.'
    prefix = f"^[{re.escape(prefixes)}]"
    return filters.sudoers & filters.regex(prefix+command, *args, **kwargs)

pyrogram.filters.sudoers = filters.create(filter_sudoers, 'FilterSudoers')
pyrogram.filters.su_cmd = filter_su_cmd
pyrogram.types.CallbackQuery.edit = query_edit
pyrogram.types.Message.remove_keyboard = remove_keyboard
pyrogram.types.Message.reply = reply_text
pyrogram.types.Message.edit = edit_text

# I don't use os.getenv('KEY', fallback) because the fallback wil only be used if the key doesn't exist. I want to use the fallback also when the key exists but it's invalid
client = Client(os.getenv('PYROGRAM_SESSION') or 'client', plugins={"root":"handlers"}, **pyrogram_config)
client.set_parse_mode('html')

def open_yml(filename):
    with open(filename) as fp:
        data = yaml.safe_load(fp)
    return data

strings = {}
for string_file in glob.glob('strings/*.yml'):
    language_code = re.match('strings/(.+)\.yml$', string_file)[1]
    strings[language_code] = open_yml(string_file)

langs = Langs(**strings, escape_html=True)

bot = Client('bot', plugins={"root": "bot_handlers"}, bot_token=os.getenv('BOT_TOKEN'), **pyrogram_config)

cmds = ['upgrade', 'restart', 'eval', 'exec', 'cmd', 'ping', 'help', 'settings']
cmds = {x:1 for x in cmds} # i transform it into a dict to make it compatible with userlixo-rfc plugins
plugins = {}