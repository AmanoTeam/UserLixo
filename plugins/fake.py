import os

from pyrogram import Client, filters
from pyrogram.errors import (
    BadRequest,
    PeerIdInvalid,
    UsernameInvalid,
    UsernameNotOccupied,
)
from pyrogram.raw import functions
from pyrogram.raw.types.users import UserFull
from pyrogram.types import Message

from config import cmds
from db import db, save


@Client.on_message(filters.command("fake", prefixes=".") & filters.me)
async def fake(client: Client, message: Message):
    text = message.text[6:]
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif not text:
        user_id = (await client.get_me()).id
    else:
        user_id = int(text) if text.lstrip("-").isdigit() else text

    try:
        cha: UserFull = await client.invoke(
            functions.users.GetFullUser(id=await client.resolve_peer(user_id))
        )
    except (UsernameInvalid, UsernameNotOccupied):
        return await message.edit(f"invalid username @{user_id}.")
    except PeerIdInvalid:
        return await message.edit("This user is not in my database.")
    except BadRequest:
        return await message.edit("only works with profiles.")

    if not db["personal_data"]["faked"]:
        info = await client.get_chat("me")
        personal_data = dict(
            first_name=info.first_name,
            last_name=info.last_name or "",
            description=info.bio or "",
            faked=False,
            user_photo=False,
        )

        db["personal_data"] = personal_data
        save(db)
    if db["personal_data"]["user_photo"]:
        async for photo in client.get_chat_photos("me", limit=1):
            await client.delete_profile_photos(photo.file_id)
        db["personal_data"]["user_photo"] = False
        save(db)
    if cha.users[0].is_self:
        dat = db["personal_data"]
        db["personal_data"]["faked"] = False
        save(db)
        text = "No fake"
    else:
        bio_offset = 70
        if len(cha.full_user.about) > bio_offset:
            me = await client.get_me()
            if me.is_premium:
                bio_offset = 140

        text = "new fake"
        if cha.full_user.about:
            description = cha.full_user.about[:bio_offset]
        else:
            description = ""
        db["personal_data"]["faked"] = True
        save(db)
        if cha.users[0].photo:
            async for photo in client.get_chat_photos(user_id, limit=1):
                media = await client.download_media(photo.file_id)
                await client.set_profile_photo(photo=media)
                os.remove(media)
            db["personal_data"]["user_photo"] = True
            save(db)
        dat = dict(
            first_name=cha.users[0].first_name,
            last_name=cha.users[0].last_name or "",
            description=description,
        )
    await client.update_profile(
        first_name=dat["first_name"],
        last_name=dat["last_name"],
        bio=dat["description"],
    )
    await message.edit(text)
    print(db["personal_data"])


cmds.update({".fake": "Copy the person's profile"})
