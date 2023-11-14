from pyrogram import Client, filters
from pyrogram.types import Message
from db import Notes

@Client.on_message(filters.command("note", prefixes=".") & filters.sudoers)
async def onote(c: Client, m: Message):
    parts = m.text.split(" ", 2)
    if len(parts) == 1:
        return
    elif len(parts) == 2:
        note_key = parts[1]

        if m.reply_to_message:
            await Notes.get_or_create(name=note_key)
            msg = m.reply_to_message
            if msg.text:
                await Notes.get(name=note_key).update(content=msg.text)
                await Notes.get(name=note_key).update(type="text")
                await m.edit(f"Note {note_key} saved")
            elif msg.media:
                media = (
                    msg.audio
                    or msg.document
                    or msg.photo
                    or msg.sticker
                    or msg.video
                    or msg.animation
                    or msg.voice
                    or msg.video_note
                )
                if not media:
                    return await m.edit("Non-supported media")
                await Notes.get(name=note_key).update(file=media.file_id)
                await Notes.get(name=note_key).update(type="media")
                await Notes.get(name=note_key).update(content=msg.caption if msg.caption else "")

                await m.edit(f"Note {note_key} saved")
        else:
            exists = await Notes.get_or_none(name=note_key)
            if exists:
                if exists.type == "text":
                    await m.edit(exists.content)
                elif exists.type == "media":
                    await m.delete()
                    await c.send_cached_media(
                        m.chat.id,
                        exists.file
                    )

@Client.on_message(filters.regex("^#") & filters.sudoers)
async def onsharp(c: Client, m: Message):
    note_key = m.text[1:]
    exists = await Notes.get_or_none(name=note_key)

    if exists:
        if exists.type == "text":
            text = exists.content
            msg = await m.edit(text)
            if text.startswith(".exec"):
                from plugins.user.execs import execs

                await execs(c, msg)
        elif exists.type == "media":
            await m.delete()
            await c.send_cached_media(
                m.chat.id,
                exists.file,
                reply_to_message_id=(
                    m.reply_to_message.id
                    if m.reply_to_message
                    else None
                ),
            )
