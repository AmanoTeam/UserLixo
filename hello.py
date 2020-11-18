"""
hello.py (v1.0)

This plugin sends a "Hello!" when you send the command .hi

Author: @usernein
Channel: @hpxlist
GitHub: <a href='github.com/usernein'>usernein</a>
"""
from pyrogram import Client, filters

@Client.on_message(filters.su_cmd('hi'))
async def on_hi(c, m):
    await m.reply('Hello!')
