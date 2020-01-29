from pyrogram import Client, Filters
import subprocess
import re

@Client.on_message(Filters.command("cmd", prefixes=".") & Filters.me)
def cmd(client, message):
    text = message.text[5:]
    res = subprocess.getstatusoutput(text)[1] or 'Comando execultado'
    message.edit(res)