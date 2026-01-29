from hydrogram import Client, filters
from hydrogram.types import Message

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
                await Notes.get(name=note_key).update(
                    content=msg.caption if msg.caption else ""
                )

                await m.edit(f"Note {note_key} saved")
        else:
            exists = await Notes.get_or_none(name=note_key)
            if exists:
                if exists.type == "text":
                    await m.edit(exists.content)
                elif exists.type == "media":
                    await m.delete()
                    await c.send_cached_media(m.chat.id, exists.file)

@Client.on_message(filters.command("notes", prefixes=".") & filters.sudoers)
async def onotes(c: Client, m: Message):
    notes = await Notes.all()
    if not notes:
        return await m.edit("No notes saved")
    note_list = "Saved notes:\n\n"
    for note in notes:
        note_list += f"- {note.name} ({note.type})\n"
    await m.edit(note_list)


@Client.on_message(filters.regex("^#") & filters.sudoers)
async def onsharp(c: Client, m: Message):
    # Suporte a input extra após o note_key
    if " " in m.text:
        note_key, input_value = m.text[1:].split(" ", 1)
    else:
        note_key, input_value = m.text[1:], None
    exists = await Notes.get_or_none(name=note_key)

    if exists:
        if exists.type == "text":
            text = exists.content
            msg = await m.edit(text)
            if text.startswith(".exec"):
                from plugins.user.execs import execs

                # Passa input_value como argumento extra para execs
                if input_value:
                    msg.text += f"\n\n#input={input_value}"
                await execs(c, msg)
        elif exists.type == "media":
            await m.delete()
            await c.send_cached_media(
                m.chat.id,
                exists.file,
                reply_to_message_id=(
                    m.reply_to_message.id if m.reply_to_message else None
                ),
            )

@Client.on_message(filters.command("rnote", prefixes=".") & filters.sudoers)
async def delete_note(c: Client, m: Message):
    parts = m.text.split(" ", 1)
    if len(parts) == 1:  # Usuário não forneceu a chave da nota
        return await m.edit("Please specify the note key to delete.")
    
    note_key = parts[1]
    note_to_delete = await Notes.get_or_none(name=note_key)

    if note_to_delete:  # Nota encontrada
        await note_to_delete.delete()  # Deleta a nota
        await m.edit(f"Note {note_key} has been deleted.")
    else:  # Nota não encontrada
        await m.edit("Note not found.")
