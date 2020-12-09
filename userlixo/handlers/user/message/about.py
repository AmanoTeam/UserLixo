from pyrogram import Client, filters

@Client.on_message(filters.su_cmd('about'))
async def on_about(c, m):
    lang = m._lang
    await m.reply(lang.about_userlixo_text, disable_web_page_preview=True)