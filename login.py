import asyncio
import base64
import configparser
import json
import os

from sys import argv

from termcolor import cprint

def raise_ex(e):
    raise e

def b64encode(value:str):
    return base64.b64encode(value.encode()).decode()
def b64decode(value:str):
    return base64.b64decode(value.encode()).decode()

config = configparser.ConfigParser()

cprint('Creating config.ini...', 'green')
if os.path.exists('config.ini'):
    config.read('config.ini')
    cprint("Loaded existing config.ini. Its values will be used by default.", 'yellow')
elif os.path.exists(os.path.expanduser('~/.pyrogramrc')):
    config.read(os.path.expanduser('~/.pyrogramrc'))
    cprint("Loaded ~/.pyrogramrc. Its values will be used by default.", 'yellow')

config.setdefault('pyrogram', {})

fields = ['api_id', 'api_hash', 'bot_token'];
if len(argv) > 1 and argv[1] == 'user':
    fields.pop()

for key in fields:
    ask_text = f"\nType your {key}"
    if key in config['pyrogram']:
        default_value = config['pyrogram'][key]
        ask_text += f" (default: {default_value})"
    ask_text += "\n>>> "
    value = input(ask_text)
    
    if not value:
        if key not in config['pyrogram']:
            raise ValueError(f"Invalid value for {key}")
        value = default_value
        cprint(f"    Default value used: {value}", 'yellow')
    
    config['pyrogram'][key] = value

with open('config.ini','w') as fp:
    config.write(fp)

async def init():
    cprint('\nLogging in and creating new .session file...', 'green')
    if os.path.exists('client.session'):
        os.remove('client.session')
    from pyrogram import Client
    client = Client('client', plugins={'enabled':False})
    await client.start()
    
    session_config = {k:v for section in config.sections() for k,v in config.items(section)}
    session_config = json.dumps(session_config)
    session_config = b64encode(session_config)
    
    session_string = client.export_session_string()
    
    me = await client.get_me()
    mention = f"@{me.username}" if me.username else me.first_name
    cprint(f"Logged in as {mention}", 'green')
    
    print("\nYour PYROGRAM_CONFIG (SENSITIVE DATA, DO NOT SHARE):")
    cprint(session_config, 'blue')
    
    print("\nYour PYROGRAM_SESSION (SENSITIVE DATA, DO NOT SHARE):")
    cprint(session_string+"\n", 'blue')
    
    await client.stop()

asyncio.run(init())
cprint("Done.", 'green')