from pyrogram import Client, Filters
from pyrogram.api import functions
import config
import os

@Client.on_message(Filters.command("fake", prefix = ['!','/']))
def fake(client,message):
    if message.from_user.id in config.sudos:
        text = message.text[6:]
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
        else:
            if text == '':
                user_id = client.get_me().id
            else:
                try:
                    user_id = int(text)
                except:
                    user_id = text
        cha = client.get_chat(user_id)
        if cha.type == 'private' or cha.type == 'bot':
            elif cha.id == client.get_me().id:
                dat = config.personal_data
                text = 'No fake'
            else:
                text = 'new fake'
                if cha.description:
                    description = cha.description[:69]
                else:
                    description = ''
                if cha.last_name:
                    last_name = cha.last_name
                else:
                    last_name = ''
                dat = {
                        'pic':client.get_profile_photos(user_id, limit=1)[0].file_id,
                        'description':description,
                        'last_name':last_name,
                        'first_name':cha.first_name
                        }
            client.send(
                    functions.account.UpdateProfile(
                        first_name=dat['first_name'], last_name=dat['last_name'],
                        about=dat['description']
                        )
                    )
            try:
                a = client.download_media(dat['pic'])
                client.set_profile_photo(a)
                os.remove(a)
            except:
                pass
            message.reply(text)
        else:
            message.reply('only works with profiles')
