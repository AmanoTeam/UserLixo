import os
import sys
import asyncio
import configparser

from pyrogram import Client

print('Creating config.ini...')

config = configparser.ConfigParser()
config['pyrogram'] = {}    
config['pyrogram']['api_id'] = sys.argv[1] if 1 < len(sys.argv) else input('api_id: ')
config['pyrogram']['api_hash'] = sys.argv[2] if 2 < len(sys.argv) else input('api_hash: ')
config['plugins'] = {}
config['plugins']['root'] = 'plugins'

with open('config.ini','w') as fp:
    config.write(fp)

async def init():
    print('Logging in and creating .session file...')
    client = Client('my_account', config['pyrogram']['api_id'], config['pyrogram']['api_hash'])
    await client.start()
    await client.stop()

loop = asyncio.get_event_loop()
if not os.path.exists('my_account.session'):
    loop.run_until_complete(init())
print(f"Done. Now install the requirements (if not installed yet) and run '{os.path.basename(sys.executable)} bot.py'.")
