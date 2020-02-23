import html
import os
import json

from pyrogram import Client, Filters
from config import cmds
from db import db, save

@Client.on_message(Filters.command("note", prefixes=".") & Filters.me)
async def onnote(client, message):
    parts = message.text.split(' ', 2)
    if len(parts) == 1:
        return
    elif len(parts) == 2:
        note_key = parts[1]
        exists = note_key in db['notes']
        
        if message.reply_to_message:
            msg = message.reply_to_message
            if msg.text:
                note_obj = dict(type='text', value=msg.text)
            else:
                return await message.edit('Saving nontextual notes is not supported yet')
            
            db['notes'][note_key] = note_obj
            save(db)
            action = 'updated' if exists else 'created'
            await message.edit(f"Note '<code>{html.escape(note_key)}</code>' {action}.")
        else:
            if exists:
                note_obj = db['notes'][note_key]
                if note_obj['type'] == 'text':
                    await message.edit(note_obj['value'])
            else:
                await message.edit(f"There isn't a note named '<code>{html.escape(note_key)}</code>'.")
    else:
        note_key = parts[1]
        note_value = parts[2]
        exists = note_key in db['notes']
        
        note_obj = dict(type='text', value=note_value)
        
        db['notes'][note_key] = note_obj
        save(db)
        action = 'updated' if exists else 'created'
        await message.edit(f"Note '<code>{html.escape(note_key)}</code>' {action}.")
        
@Client.on_message(Filters.command("notes", prefixes=".") & Filters.me)
async def onnotes(client, message):
    notes = db['notes']
    
    parts = message.text.split(' ', 2)
    if len(parts) == 1:
        if not len(notes):
            await message.edit("No notes have been created yet.")
        else:
            text = "\n".join(['<code>%s</code>'.format(html.escape(note_key)) for note_key in notes.keys()])
            await message.edit(text)
    else:
        command = parts[1]
        if command == 'backup':
            with open('notes.json', 'w') as fp:
                json.dump(notes, fp, indent=2)
            await client.send_document("me", document="notes.json")
            os.remove('notes.json')
            await message.edit("notes.json sent to Saved Messages.")

@Client.on_message(Filters.regex("^#") & Filters.me)
async def onsharp(client, message):
    note_key = message.text[1:]
    exists = note_key in db['notes']
    
    if exists:
        note_obj = db['notes'][note_key]
        if note_obj['type'] == 'text':
            await message.edit(note_obj['value'])

cmds.update({
    "note": "Add/update a note",
    "notes": "List the saved notes. Pass 'backup' as argument to get a backup file",
    "#<note>": html.escape("Get a note. Replace '<note>' with the note key")
})