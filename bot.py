import asyncio
import os
import sys

from pyrogram import idle

import config
from db import db, save


async def run_client(client):
    try:
        await client.start()
    except AttributeError as e:
        return print(
            str(e).split(". ")[0]
            + f". Run '{os.path.basename(sys.executable)} setup.py' first."
        )

    if "restart" in db:
        text = "Restarted"
        if "branch" in db["restart"]:
            text += (
                f". Upgraded from the branch '<code>{db['restart']['branch']}</code>'"
            )
        await client.edit_message_text(db["restart"]["cid"], db["restart"]["mid"], text)
        del db["restart"]
        save(db)

    # Saving the account data on startup
    try:
        info = await client.get_chat("me")
        personal_data = dict(
            first_name=info.first_name,
            last_name=info.last_name or "",
            description=info.bio or "",
            faked=False,
            user_photo=False,
        )

        db["personal_data"] = personal_data
        save(db)
        print("Personal account data updated!")
    except Exception as e:
        print(f"Could not save the personal account data on startup. Cause: {e}")

    await idle()
    await client.stop()


loop = asyncio.get_event_loop()
loop.run_until_complete(run_client(config.app))
