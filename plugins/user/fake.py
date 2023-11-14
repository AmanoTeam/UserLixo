from pyrogram import Client, filters
from pyrogram.types import Message
from locales import use_lang
from db import Fake
from pyrogram.enums import MessageEntityType
import os
from pyrogram import types
import re

# This function is triggered when the ".fake" command is sent by a sudoer
@Client.on_message(filters.command("fake", prefixes=".") & filters.sudoers)
@use_lang()
async def fake(c:Client, m: Message, t):
    # Get or create a Fake object with id=0
    await Fake.get_or_create(id=0)
    
    # If the user is not faked, save the user
    if not (await Fake.get(id=0)).faked:
        await save_user(c)
    
    p = None
    texto = None
    
    # Check if the message is a reply to another message
    if m.reply_to_message:
        user_id = m.reply_to_message.from_user.id
    # Check if the message contains a text mention
    elif m.entities and m.entities[0].type == MessageEntityType.TEXT_MENTION:
        user_id = m.entities[0].user.id
    # Check if the message contains a user id
    elif len(m.text.split(" ", 1)) > 1:
        match = re.search(r'\.fake\s*(-\w+)?\s*(.*)', m.text, re.IGNORECASE)
        
        print(match)

        if match:
            p = match.group(1) if match.group(1) else None
            user_id = match.group(2) if match.group(2) else None
            print(p, user_id)

    else:
        user_id = c.me.id
    usr = await c.get_users(user_id)
    
    em = await m.edit(t("fake_init").format(mention=usr.mention))
    
    if usr.is_self:
        await em.edit(t("fake_back"))
        
        sel = await Fake.get(id=0)
        
        await c.update_profile(
            first_name=sel.first_name,
            last_name=sel.last_name,
            bio=sel.description
        )
        print(sel.user_photo)
        if sel.user_photo:
            async for photo in c.get_chat_photos("me", limit=1):
                await c.delete_profile_photos(photo.file_id)
        
        if sel.emoji_status:
            await c.set_emoji_status(
                types.EmojiStatus(custom_emoji_id=sel.emoji_status)
            )
        
        await Fake.get(id=0).update(faked=False, user_photo=False)
        
    else:
        await Fake.get(id=0).update(faked=True)
        
        set_photo, set_name, set_bio = False, False, False

        if p and p == "-p":
            set_photo = True
        elif p and p == "-n":
            set_name = True
        elif p and p == "-b":
            set_bio = True
        else:
            set_photo, set_name, set_bio = True, True, True
        
        if (await Fake.get(id=0)).user_photo:
            async for photo in c.get_chat_photos("me", limit=1):
                await c.delete_profile_photos(photo.file_id)
            await Fake.get(id=0).update(user_photo=False)

        if usr.photo and set_photo:
            async for photo in c.get_chat_photos(usr.id, limit=1):
                media = await c.download_media(photo.file_id)
                await c.set_profile_photo(photo=media)
                os.remove(media)
            await Fake.get(id=0).update(user_photo=True)
        
        bio_offset = 140 if c.me.is_premium else 70
        
        print(usr)
        
        userc = await c.get_chat(user_id)
        
        await c.update_profile(
            first_name=usr.first_name if set_name else None,
            last_name=(usr.last_name if usr.last_name else "") if set_name else None,
            bio=(userc.bio[:bio_offset] if userc.bio else "") if set_bio else None
        )
        
        if usr.emoji_status and c.me.is_premium:
            await c.set_emoji_status(
                types.EmojiStatus(custom_emoji_id=usr.emoji_status.custom_emoji_id)
            )
        elif c.me.is_premium:
            await c.set_emoji_status(
                types.EmojiStatus(custom_emoji_id=6043929741877055318)
            )
        
        await em.edit(t("fake_done").format(mention=usr.mention))


async def save_user(c: Client):
    usr = await c.get_me()
    userc = await c.get_chat("me")
    first_name = usr.first_name
    last_name = usr.last_name if usr.last_name else ""
    description = userc.bio if userc.bio else ""

    await Fake.get(id=0).update(
        first_name=first_name,
        last_name=last_name,
        description=description,
        user_photo=False
    )
    print(usr)
    if usr.emoji_status:
        await Fake.get(id=0).update(emoji_status=usr.emoji_status.custom_emoji_id)
