from db import db, save
import asyncio

print('Configurando...')
with open('config.py.example') as fp:
    con = fp.read()
    
api_id = input('api_id: ')
api_hash = input('api_hash: ')

con = con.format(api_id=api_id, api_hash=api_hash)

with open('config.py','w') as fp:
    fp.write(con)

from config import app

async def init():
    print('Login')
    await app.start()
    await app.stop()

loop = asyncio.get_event_loop()
loop.run_until_complete(init())
