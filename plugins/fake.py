import os

from pyrogram import Client, Filters
from pyrogram.api import functions
from pyrogram.errors import BadRequest, UsernameNotOccupied, UsernameInvalid, PeerIdInvalid

from db import db, save
from config import cmds


@Client.on_message(Filters.command("fake", prefixes=".") & Filters.me)
async def fake(client, message):
    text = message.text[6:]
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif not text:
        user_id = (await client.get_me()).id
    else:
        user_id = int(text) if text.lstrip('-').isdigit() else text

    try:
        cha = await client.send(
            functions.users.GetFullUser(id=await client.resolve_peer(user_id))
        )
    except (UsernameInvalid, UsernameNotOccupied):
        await message.edit(f'invalid username @{user_id}.')
    except PeerIdInvalid:
        await message.edit('This user is not in my database.')
    except BadRequest:
        await message.edit('only works with profiles.')
    else:
        if cha.user.is_self:
            dat = db['personal_data']
            try:
                await client.set_profile_photo(photo='avatar.jpg')
            except (BadRequest, FileNotFoundError):
                pass
            text = 'No fake'
        else:
            text = 'new fake'
            if cha.about:
                description = cha.about[:70]
            else:
                description = ''
            a = (await client.get_profile_photos(user_id, limit=1))[0]
            dat = dict(
                first_name=cha.user.first_name,
                last_name=cha.user.last_name or '',
                description=description
            )
            try:
                a = await client.download_media(a.file_id, a.file_ref)
                await client.set_profile_photo(photo=a)
                os.remove(a)
            except:
                pass
        # TODO: Switch to client.update_profile when the next pyrogram_modversion is released.
        await client.send(
            functions.account.UpdateProfile(
                first_name=dat['first_name'], last_name=dat['last_name'],
                about=dat['description']
            )
        )
        await message.edit(text)


@Client.on_message(Filters.command("savepic", prefixes=".") & Filters.me)
async def savepic(client, message):
    a = (await client.get_profile_photos("me", limit=1))[0]
    try:
        await client.download_media(a.file_id, a.file_ref, file_name='./avatar.jpg')
        b = await client.get_chat("me")
        personal_data = dict(
            first_name=b.first_name,
            last_name=b.last_name or '',
            description=b.description or ''
        )
        db['personal_data'] = personal_data
        save(db)
        await message.edit('saved')
    except Exception as e:
        await message.edit(f'not saved\n\nCause: {e}')

cmds.update({'.fake':"Copy the person's profile",
             ".savepic":"Save your profile"})
