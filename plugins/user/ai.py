import json
import os
import re

from EdgeGPT.EdgeGPT import Chatbot, ConversationStyle
from pyrogram import Client, filters
from pyrogram.types import Message, InputMediaPhoto
from BingImageCreator import ImageGen
import io
from utils import http
from locales import use_lang
import requests
from bardapi import Bard
import markdown
from telegraph.aio import Telegraph

bing_instances = {}
bard_instances = {}

telegraph = Telegraph()

async def filter_bing_logic(flt, client:Client, message: Message):
    if message:
        if message.reply_to_message_id and message.reply_to_message_id in bing_instances:
            return True
        else:
            return False

filter_bing = filters.create(filter_bing_logic)

async def filter_bard_logic(flt, client:Client, message: Message):
    if message:
        if message.reply_to_message_id and message.reply_to_message_id in bard_instances:
            return True
        else:
            return False

filter_bard = filters.create(filter_bard_logic)

# This function is triggered when the ".bing" command is sent by a sudoer
@Client.on_message((filters.command("bing", prefixes=".") | filter_bing) & filters.sudoers)
@use_lang()
async def bing(c: Client, m: Message, t):
    try:
        if (m.reply_to_message_id and m.reply_to_message_id in bing_instances):
            bot = bing_instances.pop(m.reply_to_message_id)
            mtext = m.text
        else:
            bot = await Chatbot.create(cookies=json.load(open('./cookies.json', 'r', encoding='utf-8'))) if os.path.exists('./cookies.json') else await Chatbot.create()
            mtext = m.reply_to_message.text if m.reply_to_message and m.reply_to_message.text else m.reply_to_message.caption if m.reply_to_message else m.text.split(".bing ", maxsplit=1)[1]
            if m.reply_to_message and len(m.text.split(" ", maxsplit=1)) >= 2:
                mtext = m.text.split(" ", maxsplit=1)[1] + "\n" + f"\"{mtext}\""

        await m.edit(t("ai_bing_searching").format(text=mtext))
        response = await bot.ask(prompt=mtext, conversation_style=ConversationStyle.creative, simplify_response=True)
        text = f'<pre>{mtext}</pre>\n\n{response["text"]}'
        links = re.findall(r'\[(\d+)\.\s(.*?)\]\((.*?)\)', response["sources_text"])
        for link in links:
            text = text.replace(f"[^{link[0]}^]", f'<a href="{link[2]}">[{link[0]}]</a>')

        if len(text) > 4096:
            await telegraph.create_account(short_name="EdgeGPT")
            text = markdown.markdown(text)
            page = await telegraph.create_page(f"Bing-userlixo-{c.me.first_name}", html_content=text, author_name="EdgeGPT", author_url="https://t.me/UserLixo")
            m = await m.edit(f'<pre>{mtext}</pre>\n\n{page["url"]}')
        else:
            m = await m.edit(text, disable_web_page_preview=True)
        
        bing_instances[m.id] = bot
    except Exception as e:
        await m.edit(str(e))

# This function is triggered when the ".bingimg" command is sent by a sudoer
@Client.on_message(filters.command("bingimg", prefixes=".") & filters.sudoers)
@use_lang()
async def bingimg(c: Client, m: Message, t):
    text = m.text.split(" ", maxsplit=1)[1] if len(m.text.split(" ", maxsplit=1)) >= 2 else m.reply_to_message.text if m.reply_to_message else None
    if not text:
        return await m.edit(t("ai_no_text"))

    await m.edit(t("ai_making_image").format(text=text))
    cookies = json.load(open('./cookies.json', 'r', encoding='utf-8'))
    cookie_u = next((cookie["value"] for cookie in cookies if cookie["name"] == "_U"), None)
    cookie_SRCHHPGUSR = next((cookie["value"] for cookie in cookies if cookie["name"] == "SRCHHPGUSR"), None)
    img_gen = ImageGen(auth_cookie=cookie_u, auth_cookie_SRCHHPGUSR=cookie_SRCHHPGUSR, quiet=True, all_cookies=cookies)

    try:
        urls = img_gen.get_images(str(text))
    except Exception as e:
        return await m.edit(str(e))

    photos = [InputMediaPhoto(io.BytesIO((await http.get(i)).content), caption=text if n == 0 else None) for n, i in enumerate(urls)]
    if m.reply_to_message:
        if m.from_user.is_self:
            await m.delete()
        await m.reply_to_message.reply_media_group(photos)
    else:
        await m.reply_media_group(photos)

# This function is triggered when the ".bard" command is sent by a sudoer
@Client.on_message((filters.command("bard", prefixes=".") | filter_bard) & filters.sudoers)
@use_lang()
async def bardc(c: Client, m: Message, t):
    if m.reply_to_message_id and m.reply_to_message_id in bard_instances:
        bot = bard_instances[m.reply_to_message_id]
        mtext = m.text
    else:
        session = requests.Session()
        session_cookies = json.load(open("bard_coockies.json", "r"))
        secure_1psid = next((cookie["value"] for cookie in session_cookies if cookie["name"] == "__Secure-1PSID"), None)

        for cookie in session_cookies:
            session.cookies.set(cookie["name"], cookie["value"], domain=cookie["domain"], path=cookie["path"])

        session.headers = {
            "Host": "bard.google.com",
            "X-Same-Domain": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.4472.114 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Origin": "https://bard.google.com",
            "Referer": "https://bard.google.com/",
        }

        bot = Bard(session=session, token=secure_1psid)
        mtext = m.reply_to_message.text if m.reply_to_message and m.reply_to_message.text else m.reply_to_message.caption if m.reply_to_message else m.text.split(" ", maxsplit=1)[1]

    await m.edit(t("ai_bard_searching").format(text=mtext))
    response = bot.get_answer(mtext)
    text = f'<pre>{mtext}</pre>\n\n{response["content"]}'

    if len(text) > 4096:
        await telegraph.create_account(short_name="Bard")
        text = markdown.markdown(text)
        for i in range(text.count("[Image of")):
            inicio = text.index("[Image of")
            fim = text.index("]", inicio) + 1
            text = text[:inicio] + f"<img src='{response['images'][i]}'>" + text[fim:]
        page = await telegraph.create_page(f"Bard-userlixo-{c.me.first_name}", html_content=text, author_name="Bard", author_url="https://t.me/UserLixo")
        m = await m.edit(f'<pre>{mtext}</pre>\n\n{page["url"]}')
    elif response["images"]:
        photos = [InputMediaPhoto(io.BytesIO((await http.get(i)).content), caption=text[:4096] if n == 0 else None) for n, i in enumerate(response["images"])]
        m = await m.reply_media_group(photos)
    else:
        m = await m.edit(text[:4096])

    bard_instances[m.id] = bot
