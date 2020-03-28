import asyncio
import databases
import orm
import os
import sqlalchemy
import threading

from functools import partial
from orm import Model, JSON, DateTime, Integer, String
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker


database = databases.Database(os.getenv('DATABASE_URL'))
metadata = sqlalchemy.MetaData()

class Info(Model):
	__tablename__ = 'info'
	__database__ = database
	__metadata__ = metadata
	
	key = Integer(primary_key=True)
	restart_info = JSON(default='{"chat_id": "", "message_id": ""}')
	profile = JSON(default='{"first_name": "", "last_name": "", "bio": "", "photo": ""}')
	notes = JSON(default='{}')
	timezone = String(default='America/Sao_Paulo')

engine = sqlalchemy.create_engine(str(database.url))
metadata.create_all(engine, checkfirst=True)

Session = sessionmaker(bind=engine)
session = Session()

async def create_db():
	return await database.connect()

# Need to run asyncio.run_coroutine_threadsafe with a loop in another thread. Otherwise this block will get stuck forever.
# I create a new loop to be able to use run_forever() and then stop() without affecting our main loop
loop = asyncio.get_event_loop()
threading.Thread(target=partial(asyncio.run_coroutine_threadsafe, create_db(), loop), daemon=True).start()
