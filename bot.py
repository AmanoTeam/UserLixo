import config
import asyncio
from db import db, save

async def run_client():
    await config.app.start()
    if "restart" in db:
        text = 'Restarted'
        if 'branch' in db['restart']:
            text += f". Upgraded from the branch '<code>{db['restart']['branch']}</code>'"
        await config.app.edit_message_text(db["restart"]["cid"], db["restart"]["mid"], text)
        del db["restart"]
        save(db)
    
    # Saving the account data on startup
    a = (await config.app.get_profile_photos("me", limit=1))[0]
    try:
        await config.app.download_media(a.file_id, a.file_ref, file_name='./avatar.jpg')
        b = await config.app.get_chat("me")
        personal_data = dict(
            first_name=b.first_name,
            last_name=b.last_name or '',
            description=b.description or ''
        )
        db['personal_data'] = personal_data
        save(db)
        print('Personal account data updated!')
    except Exception as e:
        print(f'Could not save the personal account data on startup. Cause: {e}')
        
    await config.app.idle()

loop = asyncio.get_event_loop()
loop.run_until_complete(run_client())