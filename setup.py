import asyncio
import os
import sys

from pyrogram import Client

print("Creating config.py...")

config = open("config.py.example", "r").read()

api_id = sys.argv[1] if 1 < len(sys.argv) else input("api_id: ")
api_hash = sys.argv[2] if 2 < len(sys.argv) else input("api_hash: ")

config = config.replace("api_id_here", api_id).replace("api_hash_here", api_hash)

with open("config.py", "w") as fp:
    fp.write(config)


async def init():
    print("Logging in and creating .session file...")
    client = Client(
        "my_account", config["pyrogram"]["api_id"], config["pyrogram"]["api_hash"]
    )
    await client.start()
    await client.stop()

if not os.path.exists("my_account.session"):
    event_policy = asyncio.get_event_loop_policy()
    loop = event_policy.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(init())
print(
    f"Done. Now install the requirements (if not installed yet) and run '{os.path.basename(sys.executable)} bot.py'."
)
