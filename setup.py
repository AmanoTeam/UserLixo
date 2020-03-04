import asyncio
import configparser

from pyrogram_mod import Client

print('Creating config.ini...')

config = configparser.ConfigParser()
config['pyrogram'] = {}    
config['pyrogram']['api_id'] = input('api_id: ')
config['pyrogram']['api_hash'] = input('api_hash: ')
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
loop.run_until_complete(init())
print('Done.')