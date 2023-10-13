import json
import os
import re

from EdgeGPT.EdgeGPT import Chatbot, ConversationStyle
from pyrogram import Client, filters
from pyrogram.types import Message

from config import cmds


@Client.on_message(filters.command("bing", prefixes=".") & filters.me)
async def bing(c: Client, m: Message):
    try:
        if os.path.exists('./cookies.json'):
            with open('./cookies.json', 'r', encoding='utf-8') as f:
                bot = await Chatbot.create(cookies=json.load(f))
        else:
            bot = await Chatbot.create()

        if m.reply_to_message:
            mtext = m.reply_to_message.text
        else:
            mtext = m.text.split(".bing ", maxsplit=1)[1]

        response = await bot.ask(prompt=mtext, conversation_style=ConversationStyle.creative, simplify_response=True)
        text = response["text"]
        links = re.findall(r'\[(\d+)\.\s(.*?)\]\((.*?)\)',
                           response["sources_text"])
        for link in links:
            text = text.replace(
                f"[^{link[0]}^]", f'<a href="{link[2]}">[{link[0]}]</a>')

        await m.edit(f'"{mtext}":\n{text}'[:4096], disable_web_page_preview=True)

        await bot.close()
    except Exception as e:
        await m.edit(str(e))

cmds.update({".bing": "ChatBing Search"})
