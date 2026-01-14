#!/usr/bin/env python3
"""
Script to create Telegram sessions (bot.session and user.session)
Run this script once to authenticate the bot and userbot.
"""
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Sessions directory (absolute path)
SESSIONS_DIR = Path("/app/sessions")
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

try:
    API_ID = int(os.environ.get("API_ID"))
    API_HASH = os.environ.get("API_HASH")
except (TypeError, ValueError):
    print("\n############################################################")
    print("ERROR: API_ID and API_HASH not found!")
    print("Make sure the .env file exists with the credentials.")
    print("############################################################\n")
    exit(1)

async def setup_bot():
    """Setup bot session (requires BotFather token)"""
    from hydrogram import Client
    
    print("\n" + "="*60)
    print("BOT SETUP")
    print("="*60)
    print("You will need the bot token from @BotFather")
    print("-"*60 + "\n")
    
    session_path = str(SESSIONS_DIR / "bot")
    bot = Client(session_path, api_id=API_ID, api_hash=API_HASH)
    await bot.start()
    me = await bot.get_me()
    print(f"\n✅ Bot configured successfully!")
    print(f"   Name: {me.first_name}")
    print(f"   Username: @{me.username}")
    print(f"   Session: {session_path}.session")
    await bot.stop()

async def setup_user():
    """Setup userbot session (requires phone number)"""
    from hydrogram import Client
    
    print("\n" + "="*60)
    print("USERBOT SETUP")
    print("="*60)
    print("You will need your phone number and verification code")
    print("-"*60 + "\n")
    
    session_path = str(SESSIONS_DIR / "user")
    user = Client(session_path, api_id=API_ID, api_hash=API_HASH)
    await user.start()
    me = await user.get_me()
    print(f"\n✅ Userbot configured successfully!")
    print(f"   Name: {me.first_name} {me.last_name or ''}")
    print(f"   ID: {me.id}")
    print(f"   Session: {session_path}.session")
    await user.stop()

async def main():
    print("\n" + "#"*60)
    print("#" + " "*20 + "USERLIXO SETUP" + " "*24 + "#")
    print("#"*60)
    print("\nThis script will create the necessary session files.")
    print("You will need to provide credentials interactively.\n")
    print(f"Sessions directory: {SESSIONS_DIR}")
    
    # Check which sessions already exist
    bot_session = SESSIONS_DIR / "bot.session"
    user_session = SESSIONS_DIR / "user.session"
    bot_exists = bot_session.exists()
    user_exists = user_session.exists()
    
    if bot_exists and user_exists:
        print("⚠️  Both sessions already exist!")
        resp = input("Do you want to recreate them? (y/N): ").strip().lower()
        if resp != 'y':
            print("Cancelled.")
            return
    
    # Bot Setup
    if not bot_exists or (bot_exists and input("\n🤖 Configure BOT? (Y/n): ").strip().lower() != 'n'):
        try:
            await setup_bot()
        except Exception as e:
            print(f"\n❌ Error configuring bot: {e}")
    
    # Userbot Setup
    if not user_exists or (user_exists and input("\n👤 Configure USERBOT? (Y/n): ").strip().lower() != 'n'):
        try:
            await setup_user()
        except Exception as e:
            print(f"\n❌ Error configuring userbot: {e}")
    
    # List created files
    print("\n" + "-"*60)
    print("Files in sessions folder:")
    for f in SESSIONS_DIR.iterdir():
        print(f"  - {f.name}")
    
    print("\n" + "="*60)
    print("✅ SETUP COMPLETE!")
    print("="*60)
    print("\nNow you can run the bot with:")
    print("  docker compose up -d userlixo")
    print("\n")

if __name__ == "__main__":
    asyncio.run(main())
