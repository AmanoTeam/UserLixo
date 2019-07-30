from pyrogram import Client, Filters
import time
import json
from datetime import datetime

@Client.on_message(Filters.command(["on","off"], prefix="/"))
def on(client, message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    else:
        try:
            user_id = int(message.text.split(' ')[1])
        except:
            user_id = message.text.split(' ')[1]
    usr = client.get_users(user_id)
    if usr.is_bot:
        message.reply('does not work with bots')
    elif not usr.status.date:
        message.reply('This person has disabled your last seen')
    else:
        if usr.status.online:
            message.reply(f'{usr.first_name} is on')
        else:
            c = int(time.time()-usr.status.date)
            date = datetime.utcfromtimestamp(c).strftime('{"months":"%-m","days":"%-d","hours":"%-H","minutes":"%-M","seconds":"%-S"}')
            f'{usr.first_name} is off for: \n » **%H** Hours\n » **%M** Minutes\n » **%S** Seconds'
            frase = f'{usr.first_name} is off for: \n'
            date = json.loads(date)
            date["days"] = int(date["days"])-1
            date["months"] = int(date["months"])-1
            if date["months"] != 0:
                frase += f' » **{date["months"]}** months\n'
            if date["days"] != 0:
                frase += f' » **{date["days"]}** Days\n'
            if date["hours"] != "0":
                frase += f' » **{date["hours"]}** Hours\n'
            if date["minutes"] != "0":
                frase += f' » **{date["minutes"]}** Minutes\n'
            if date["seconds"] != "0":
                frase += f' » **{date["seconds"]}** Seconds'
            message.reply(frase)