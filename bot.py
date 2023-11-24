from pathlib import Path
import os
from pyrogram import idle
from tortoise import run_async
from config import bot, user
from version import ascii_art, version
import reload
from db import Config
import db

async def main():
    # Connect to the database
    await db.connect_database()
    # Check if the bot session file exists
    if not Path("bot.session").exists():
        # Clear the screen
        os.system("clear")
        # Print a message to prompt the bot login
        print("Login Bot:")
    # Start the bot client
    await bot.start()
    # Check if the user session file exists
    if not Path("user.session").exists():
        # Clear the screen
        os.system("clear")
        # Print a message to prompt the user login
        print("login user")
    # Start the user client
    await user.start()
    # Clear the screen
    os.system("clear")
    # Print the ascii art and the version
    print(ascii_art)
    # Get the bot and user information
    bot.me = await bot.get_me()
    user.me = await user.get_me()
    # Reload the plugins
    await reload.main()
    # Get the restart and upgrade configurations from the database
    restart = await Config.get_or_none(id="restart")
    upgrade = await Config.get_or_none(id="upgrade")
    # If the restart configuration exists and has a value
    if restart and restart.valuej:
        # Edit the message that triggered the restart to show the success message
        await user.edit_message_text(
            chat_id=restart.valuej["chat_id"],
            message_id=restart.valuej["message_id"],
            text="UserLixo Restarted!\nVersion: " + version + "\n\nBot: " + bot.me.mention + "\nUser: " + user.me.mention
        )
        # Delete the restart configuration from the database
        await Config.filter(id="restart").delete()
    # If the upgrade configuration exists and has a value
    elif upgrade and upgrade.valuej:
        # Edit the message that triggered the upgrade to show the success message
        await user.edit_message_text(
            chat_id=upgrade.valuej["chat_id"],
            message_id=upgrade.valuej["message_id"],
            text="UserLixo Upgraded!\nVersion: " + version + "\n\nBot: " + bot.me.mention + "\nUser: " + user.me.mention
        )
        # Delete the upgrade configuration from the database
        await Config.filter(id="upgrade").delete()
    # Otherwise, send a message to the user to show that the userbot has started
    else:
        await bot.send_message(user.me.id, "UserLixo Started!\nVersion: " + version + "\n\nBot: " + bot.me.mention + "\nUser: " + user.me.mention)
    # Keep the client running until it is stopped
    await idle()
    # Stop the bot and user clients
    await bot.stop()
    await user.stop()

# Run the main function asynchronously
run_async(main())
