from pyrogram import Client, Filters
from db import db

print(db["chats"])

@Client.on_message(Filters.new_chat_members)
def welcome(client, message):
    print('welcome')
    if db["chats"].get(str(message.chat.id)) and db["chats"][str(message.chat.id)].get("welcome"):
        welcome = db["chats"][str(message.chat.id)]["welcome"]
    else:
        welcome = {"power":'off',"welcome":"Hello $name, welcome to **$title**!","current":"text"}
    if welcome['current'] == 'sticker' and welcome['power'] == 'on':
        client.send_sticker(message.chat.id,welcome['sticker'],reply_to_message_id=message.message_id)
    if welcome['current'] == 'photo' and welcome['power'] == 'on':
        client.send_photo(message.chat.id,welcome['photo'],reply_to_message_id=message.message_id)
    if welcome['current'] == 'gif' and welcome['power'] == 'on':
        client.send_animation(message.chat.id,welcome['gif'],reply_to_message_id=message.message_id)
    if welcome['current'] == 'text' and welcome['power'] == 'on':
        new_members = "".join([
                "[{}](tg://user?id={})".format(i.first_name, i.id)
                for i in message.new_chat_members
			])
        welcome = welcome['welcome'].replace('$name',new_members).replace('$title',message.chat.title)
        client.send_message(message.chat.id,welcome,reply_to_message_id=message.message_id,disable_web_page_preview=True)

@Client.on_message(Filters.command("welcome", prefixes=".") & Filters.me)
def welcom(client, message):
    text = message.text.split(' ', 1)
    if message.chat.id in db and db["chats"][message.chat.id].get("welcome"):
        welcome = db["chats"][message.chat.id]["welcome"]
    else:
        welcome = {"power":'on',"welcome":"Hello $name, welcome to **$title**!","current":"text"}
    if message.reply_to_message and message.reply_to_message.sticker:
        welcome['current'] = "sticker"
        welcome['sticker'] = message.reply_to_message.sticker.file_id
        message.edit('Your welcome sticker has been successfully defined')
    elif message.reply_to_message and message.reply_to_message.photo:
        welcome['current'] = "photo"
        welcome['photo'] = message.reply_to_message.photo.sizes[-1].file_id
        message.edit('Your welcome image has been successfully defined')
    elif message.reply_to_message and message.reply_to_message.animation:
        welcome["current"] = "gif"
        welcome["gif"] = message.reply_to_message.animation.file_id
        message.edit('Your welcome GIF was successfully defined')
    elif len(text) == 1:
        message.edit('use:/n/welcome on/off/reset or the welcome message')
    elif text[1] == 'on':
        welcome['power'] = 'on'
        message.edit(message.chat.id,'welcome messages were activated')
    elif text[1] == 'reset':
        welcome = {"power":'on',"welcome":"Hello $name, welcome to **$title**!","current":"text"}
        message.edit(message.chat.id,'the welcome messages were reset')
    elif text[1] == 'off':
        welcome['power'] = 'off'
        message.edit(message.chat.id,'welcome messages have been disabled')
    else:
        text = text[1]
        welcome['current'] = "text"
        welcome['welcome'] = text
        message.edit(message.chat.id,'Your welcome message was successfully defended.')
    if not db["chats"].get(str(message.chat.id)):
        db["chats"][str(message.chat.id)] = {}
    db["chats"][str(message.chat.id)]["welcome"] = welcome
    save(db)