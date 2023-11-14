from pyrogram import Client, filters

@Client.on_message(filters.command("start", prefixes=".") & filters.sudoers)
async def start(_, message):
    await message.reply_text("Hello, World!")