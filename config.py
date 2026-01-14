import os
from hydrogram import Client

plugins = []

# Sessions directory (absolute path for Docker)
SESSIONS_DIR = "/app/sessions"

try:
    # API_ID is an integer
    API_ID = int(os.environ.get("API_ID"))
    # API_HASH is a string
    API_HASH = os.environ.get("API_HASH")

except (TypeError, ValueError) as e:
    # This exception will be raised if API_ID is not a number or if any variable is missing.
    print("\n\n############################################################")
    print("ERROR: Telegram credentials not found or invalid.")
    print("Make sure API_ID and API_HASH are correctly set in your .env file")
    print("############################################################\n")
    # To ensure the bot doesn't try to start with null credentials:
    API_ID = 0
    API_HASH = "" 


bot = Client(f"{SESSIONS_DIR}/bot", api_id=API_ID, api_hash=API_HASH, plugins=dict(root="plugins/bot"))
user = Client(f"{SESSIONS_DIR}/user", api_id=API_ID, api_hash=API_HASH, plugins=dict(root="plugins/user"))
user.assistant = bot
