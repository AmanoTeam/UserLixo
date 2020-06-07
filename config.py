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
from pyrogram import Client, Filters
from utils import tryint, query_edit, remove_keyboard, reply_text

# Load variables on config.env to os.environ
if not os.path.exists('config.env'):
    raise Exception('File config.env is missing')
load_dotenv('config.env')

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
environment_vars = ['DATABASE_URL', 'LOGS_CHAT', 'SUDOERS_LIST', 'LANGUAGE', 'BOT_TOKEN']

async def load_env():
    if not os.getenv('LOGS_CHAT'):
        os.environ['LOGS_CHAT'] = 'me'
    if not os.getenv('LANGUAGE'):
        os.environ['LANGUAGE'] = 'en'
    
    for env_key in environment_vars:
        os.environ[env_key] = (await Config.get_or_create({"value": os.getenv(env_key, '')}, key=env_key))[0].value
    
    sudoers.extend(
        [*map(lambda s: s.lstrip('@').lower() if type(s) == str else s, os.getenv('SUDOERS_LIST').split())]
    )

# Extra **kwargs for creating pyrogram.Client
pyrogram_config = os.getenv('PYROGRAM_CONFIG') or b64encode('{}')
pyrogram_config = b64decode(pyrogram_config)
pyrogram_config = json.loads(pyrogram_config)

# All monkeypatch stuff must be done before the Client instance is created
def filter_sudoers(flt, update):
    if not update.from_user:
        return
    user = update.from_user
    return user.id in sudoers or (user.username and user.username.lower() in sudoers)

pyrogram.client.filters.Filters.sudoers = Filters.create(filter_sudoers)
pyrogram.client.types.CallbackQuery.edit = query_edit
pyrogram.client.types.Message.remove_keyboard = remove_keyboard
pyrogram.client.types.Message.reply = reply_text

# I don't use os.getenv('KEY', fallback) because the fallback wil only be used if the key doesn't exist. I want to use the fallback also when the key exists but it's invalid
client = Client(os.getenv('PYROGRAM_SESSION') or 'client', plugins={"root":"plugins"}, **pyrogram_config)
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

bot = Client('bot', plugins={"root": "bot_plugins"}, bot_token=os.getenv('BOT_TOKEN'))