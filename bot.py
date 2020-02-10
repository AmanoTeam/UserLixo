import config
import asyncio
from db import db, save

async def run_client():
	await config.app.start()
	if "restart" in db:
	    await config.app.edit_message_text(db["restart"]["cid"], db["restart"]["mid"], 'Reiniciado')
	    del db["restart"]
	    save(db)
	
	await config.app.idle()

loop = asyncio.get_event_loop()
loop.run_until_complete(run_client())