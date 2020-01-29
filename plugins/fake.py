from pyrogram import Client, Filters
from pyrogram.api import functions
import config
import os

@Client.on_message(Filters.command("fake", prefixes=".") & Filters.me)
def fake(client,message):
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
        if cha.id == client.get_me().id:
            dat = config.personal_data
            try:
                client.set_profile_photo(photo='avatar.png')
            except:
                pass
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
            a = client.get_profile_photos(user_id, limit=1)[0]
            dat = {
                'description':description,
                'last_name':last_name,
                'first_name':cha.first_name
                }
            try:
                a = client.download_media(a.file_id,a.file_ref)
                client.set_profile_photo(photo=a)
                os.remove(a)
            except:
                pass
        client.send(
            functions.account.UpdateProfile(
                first_name=dat['first_name'], last_name=dat['last_name'],
                about=dat['description']
                )
            )
        message.edit(text)
    else:
        message.edit('only works with profiles')
        
@Client.on_message(Filters.command("savepic", prefixes=".") & Filters.me)
def savepic(client,message):
    a = client.get_profile_photos("me", limit=1)[0]
    try:
        client.download_media(a.file_id,a.file_ref,file_name='./avatar.png')
        message.edit('saved')
    except:
        message.edit('not saved')