import os

from pyrogram import Client, Filters
from pyrogram.api import functions

import config


@Client.on_message(Filters.command("fake", prefixes=".") & Filters.me)
def fake(client, message):
    text = message.text[6:]
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif not text:
        user_id = client.get_me().id
    else:
        user_id = int(text) if text.lstrip('-').isdigit() else text

    try:
        cha = client.get_users(user_id)
    except IndexError:
        message.edit('only works with profiles')
    else:
        if cha.is_self:
            dat = config.personal_data
            try:
                client.set_profile_photo(photo='avatar.png')
            except:
                pass
            text = 'No fake'
        else:
            text = 'new fake'
            if cha.description:
                description = cha.description[:70]
            else:
                description = ''
            a = client.get_profile_photos(user_id, limit=1)[0]
            dat = dict(
                first_name=cha.first_name,
                last_name=cha.last_name or '',
                description=description
            )
            try:
                a = client.download_media(a.file_id, a.file_ref)
                client.set_profile_photo(photo=a)
                os.remove(a)
            except:
                pass
        # TODO: Switch to client.update_profile when the next pyrogram version is released.
        client.send(
            functions.account.UpdateProfile(
                first_name=dat['first_name'], last_name=dat['last_name'],
                about=dat['description']
            )
        )
        message.edit(text)


@Client.on_message(Filters.command("savepic", prefixes=".") & Filters.me)
def savepic(client, message):
    a = client.get_profile_photos("me", limit=1)[0]
    try:
        client.download_media(a.file_id, a.file_ref, file_name='./avatar.png')
        message.edit('saved')
    except Exception as e:
        message.edit(f'not saved\n\nCause: {e}')
