import asyncio

from pyrogram import idle, Client
try:
    from config import API_ID, API_HASH
except ImportError as e:
    raise ImportError("Could not import the config file. Run 'python setup.py' first.") from e

from db import db, save


async def main():
    client = Client("my_account", api_id=API_ID, api_hash=API_HASH, plugins=dict(root="plugins"))

    await client.start()

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


event_policy = asyncio.get_event_loop_policy()
loop = event_policy.new_event_loop()
asyncio.set_event_loop(loop)

loop.run_until_complete(main())
