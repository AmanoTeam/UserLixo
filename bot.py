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
    await db.connect_database()
    if not Path("bot.session").exists():
        os.system("clear")
        print("Login Bot:")
    await bot.start()
    if not Path("user.session").exists():
        os.system("clear")
        print("login user")
    await user.start()
    os.system("clear")
    print(ascii_art)
    bot.me = await bot.get_me()
    user.me = await user.get_me()
    await reload.main()
    restart = await Config.get_or_none(id="restart")
    if restart and restart.valuej:
        await user.edit_message_text(
            chat_id=restart.valuej["chat_id"],
            message_id=restart.valuej["message_id"],
            text="UserLixo Restarted!\nVersion: " + version + "\n\nBot: " + bot.me.mention + "\nUser: " + user.me.mention
        )
        await Config.filter(id="restart").delete()
    else:
        await bot.send_message(user.me.id, "UserLixo Started!\nVersion: " + version + "\n\nBot: " + bot.me.mention + "\nUser: " + user.me.mention)
    await idle()
    await bot.stop()
    await user.stop()

run_async(main())
