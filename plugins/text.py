from pyrogram import Client, Filters

@Client.on_message(Filters.command("text", prefix = ['/','!']))
def ping(client,message):
    ch = ''
    text = message.text.split(' ',1)[1]
    if message.reply_to_message:
        message = message.reply_to_message
    ms = message.reply('`|`')
    for i in text:
        ch = ch + i
        ms.edit(f'`{ch}`')
        ms.edit(f'`{ch}|`')
    ms.edit(f'`{text}`')