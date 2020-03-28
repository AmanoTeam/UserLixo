import asyncio
import config
import os
import sys

from db import Info
from termcolor import cprint

async def run_client(client):
    try:
        await client.start()
    except AttributeError as e:
        if 'key' in str(e).lower():
            return cprint(str(e).split('. ')[0]+f". Run '{os.path.basename(sys.executable)} setup.py' first.", 'red')
        raise e
    
    if len(Info.objects.query(Info.restart_info).all()):
        text = lang.RESTARTED
        restart_info = Info.objects.query(Info.restart_info).get(1)
        
        if 'branch' in restart_info:
            text += lang.UPGRADED_FROM_BRANCH(restart_info['branch'])
        await client.edit_message_text(restart_info['chat_id'], restart_info['message_id'], text)
        restart_info.delete()
    
    # Saving the account data on startup
    photo = (await client.get_profile_photos("me", limit=1))[0]
    try:
        await client.download_media(photo.file_id, photo.file_ref, file_name='./profile_pic.jpg')
        info = await client.get_chat("me")
        p = dict(
            first_name=info.first_name,
            last_name=info.last_name or '',
            description=info.description or ''
        )
        
        db['personal_data'] = personal_data
        save(db)
        print('Personal account data updated!')
    except Exception as e:
        print(f'Could not save the personal account data on startup. Cause: {e}')
    
    await client.idle()

loop = asyncio.get_event_loop()
loop.run_until_complete(run_client(config.app))