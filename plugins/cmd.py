from pyrogram import Client, Filters
from config import sudos
import subprocess
import re

@Client.on_message(Filters.command("cmd", prefix="!"))
def cmd(client, message):
    if message.from_user.id in sudos:
        text = message.text[5:]
        if re.match('(?i).*poweroff|halt|shutdown|reboot', text):
            res = 'Comando proibido.'
        else:
            res = subprocess.getstatusoutput(text)[1] or 'Comando execultado'
        message.reply(res)