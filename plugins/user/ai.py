import json
import os
import re

from EdgeGPT.EdgeGPT import Chatbot, ConversationStyle
from pyrogram import Client, filters
from pyrogram.types import Message, InputMediaPhoto, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from BingImageCreator import ImageGen
import io
from tempfile import NamedTemporaryFile
from utils import http
from locales import use_lang
import requests
from bardapi import Bard
import markdown
from telegraph.aio import Telegraph
from config import plugins, bot
from db import Config

bing_instances = {}
bard_instances = {}

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
        if m.reply_to_message_id and m.reply_to_message_id in bing_instances:
            bot, taccount, path = bing_instances.pop(m.reply_to_message_id)
            mtext = m.text
        else:
            bot = await Chatbot.create(cookies=json.load(open('./cookies.json', 'r', encoding='utf-8'))) if os.path.exists('./cookies.json') else await Chatbot.create()
            taccount = Telegraph()
            taccount.create_account(short_name="EdgeGPT")
            path = None
            mtext = m.reply_to_message.text if m.reply_to_message and m.reply_to_message.text else m.reply_to_message.caption if m.reply_to_message else m.text.split(".bing ", maxsplit=1)[1]
            if m.reply_to_message and len(m.text.split(" ", maxsplit=1)) >= 2:
                mtext = m.text.split(" ", maxsplit=1)[1] + "\n" + f"\"{mtext}\""

        istelegraph = mtext.startswith("-t")
        mtext = mtext[3:] if istelegraph else mtext
        await m.edit(t("ai_bing_searching").format(text=f"<pre>{mtext}</pre>"))
        style = ConversationStyle.creative
        if await Config.filter(id="bing").exists():
            mode = (await Config.get(id="bing")).value
            style = ConversationStyle.balanced if mode == "balanced" else ConversationStyle.precise
        response = await bot.ask(prompt=mtext, conversation_style=style, simplify_response=True)
        links = re.findall(r'\[(\d+)\.\s(.*?)\]\((.*?)\)', response["sources_text"])
        for link in links:
            text = text.replace(f"[^{link[0]}^]", f'<a href="{link[2]}">[{link[0]}]</a>')
        ttext = markdown.markdown(response["text"])

        page_content = f'<blockquote>{mtext}</blockquote>\n\n{ttext}'
        page_title = f"EdgeGPT-userlixo-{c.me.first_name}"
        author_info = {"author_name": "EdgeGPT", "author_url": "https://t.me/UserLixo"}

        if path:
            oldt = (await taccount.get_page(path))["content"]
            page = await taccount.edit_page(path, title=page_title, html_content=oldt+page_content, **author_info)
        else:
            page = await taccount.create_page(page_title, html_content=page_content, **author_info)
        
        m = await m.edit(f'<pre>{mtext}</pre>\n\n{page["url"] if len(response["text"]) > 4096 or istelegraph else response["text"]}')
        
        bing_instances[m.id] = [bot, taccount, page["path"]]
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
        for aurl in urls:
            if aurl.endswith('.svg'):
                urls.remove(aurl)

    except Exception as e:
        return await m.edit(str(e))

    photos = [InputMediaPhoto(io.BytesIO((await http.get(i)).content), caption=text if n == 0 else None) for n, i in enumerate(urls)]
    if m.reply_to_message:
        if m.from_user.is_self:
            await m.delete()
        await m.reply_to_message.reply_media_group(photos)
    else:
        await m.reply_media_group(photos)

@Client.on_message((filters.command("bard", prefixes=".") | filter_bard) & filters.sudoers)
@use_lang()
async def bardc(c: Client, m: Message, t):
    teleimg = None
    try:
        if m.reply_to_message_id and m.reply_to_message_id in bard_instances:
            bot, taccount, path = bard_instances.pop(m.reply_to_message_id)
            mtext = m.text
        else:
            taccount = Telegraph()
            await taccount.create_account(short_name="Bard")
            path = None
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
            if m.reply_to_message and m.reply_to_message.text:
                mtext = m.reply_to_message.text
                if len(m.text.split(" ", maxsplit=1)) >= 2:
                    mtext = m.text.split(" ", maxsplit=1)[1] + "\n" + f"\"{mtext}\""
            elif m.reply_to_message and m.reply_to_message.caption:
                mtext = m.reply_to_message.caption
                if len(m.text.split(" ", maxsplit=1)) >= 2:
                    mtext = m.text.split(" ", maxsplit=1)[1] + "\n" + f"\"{mtext}\""
            else:
                mtext = m.text.split(" ", maxsplit=1)[1]

        istelegraph = mtext.startswith("-t")
        mtext = mtext[3:] if istelegraph else mtext
        isvoice = mtext.startswith("-v")
        mtext = mtext[3:] if isvoice else mtext
        await m.edit(t("ai_bard_searching").format(text=f"<pre>{mtext}</pre>"))
        if m.reply_to_message and (m.reply_to_message.photo or m.reply_to_message.sticker):
            file = await c.download_media(m.reply_to_message, in_memory=True)
            file_name = file.name
            file_bytes = bytes(file.getbuffer())
            try:
                with NamedTemporaryFile() as f:
                    f.write(file_bytes)
                    teleimg = await taccount.upload_file(f.name)
            except:
                pass
        else:
            file_bytes = None
            file_name = None
        response = bot.get_answer(mtext, image=file_bytes, image_name=file_name)
        text = f'<pre>{mtext}</pre>\n\n{response["content"]}'

        ttext = markdown.markdown(response["content"])
        for i in range(ttext.count("[Image of")):
            inicio = ttext.index("[Image of")
            fim = ttext.index("]", inicio) + 1
            ttext = ttext[:inicio] + f"<img src='{response['images'][i]}'>" + ttext[fim:]

        page_content =  f"<img src='https://telegra.ph{teleimg[0]['src']}'><br>\n\n" if teleimg else ""
        page_content += f'<blockquote>{mtext}</blockquote>\n\n{ttext}'
        page_title = f"Bard-userlixo-{c.me.first_name}"
        author_info = {"author_name": "Bard", "author_url": "https://t.me/UserLixo"}

        if path:
            oldt = (await taccount.get_page(path))["content"]
            page = await taccount.edit_page(path, title=page_title, html_content=oldt+page_content, **author_info)
        else:
            page = await taccount.create_page(page_title, html_content=page_content, **author_info)
        if isvoice:
            voice = bot.speech(response["content"])
            with NamedTemporaryFile() as f:
                f.write(bytes(voice['audio']))
                newm = m.reply_to_message if m.reply_to_message else m
                newm = await m.reply_voice(f.name, caption=f'<pre>{mtext}</pre>\n\n{page["url"]}')
            if m.from_user.is_self:
                await m.delete()
        elif len(text) > 4096 or istelegraph:
            newm = await m.edit(f'<pre>{mtext}</pre>\n\n{page["url"]}')
        elif response["images"]:
            photos = [InputMediaPhoto(io.BytesIO((await http.get(i)).content), caption=text[:4096] if n == 0 else None) for n, i in enumerate(response["images"])]
            newm = (await m.reply_media_group(photos))[0]
        else:
            newm = await m.edit(text[:4096])

        bard_instances[newm.id] = [bot, taccount, page["path"]]
    except Exception as e:
        await m.edit(str(e))

plugins.append("bing")

@bot.on_callback_query(filters.regex(r"\bconfig_plugin_bing\b"))
@use_lang()
async def config_bing(c: Client, cq: CallbackQuery, t):
    await cq.edit(t("bing_settings"), reply_markup=InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text=t("ai_mode"),
                callback_data="config_plugin_ai_mode"
            )
        ], [
            InlineKeyboardButton(
                text=t("back"),
                callback_data="config_plugins"
            )
        ]
    ]))

@bot.on_callback_query(filters.regex(r"\bconfig_plugin_ai_mode\b"))
@use_lang()
async def config_ai_mode(c: Client, cq: CallbackQuery, t):
    await cq.edit(t("ai_mode_choose"), reply_markup=InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text=t("ai_mode_creative"),
                callback_data="config_plugin_ai_mode_creative"
            ),
            InlineKeyboardButton(
                text=t("ai_mode_balanced"),
                callback_data="config_plugin_ai_mode_balanced"
            ),
            InlineKeyboardButton(
                text=t("ai_mode_precise"),
                callback_data="config_plugin_ai_mode_precise"
            )
        ] , [
            InlineKeyboardButton(
                text=t("back"),
                callback_data="config_plugin_bing"
            )
        ]
    ]))

@bot.on_callback_query(filters.regex(r"config_plugin_ai_mode_"))
@use_lang()
async def config_ai_modes(c: Client, cq: CallbackQuery, t):
    await Config.get_or_create(id="bing")
    mode = cq.data.split("_")[-1]
    if mode == "creative":
        await Config.filter(id="bing").update(value="creative")
    elif mode == "balanced":
        await Config.filter(id="bing").update(value="balanced")
    elif mode == "precise":
        await Config.filter(id="bing").update(value="precise")
    await cq.edit(t("ai_mode_changed").format(style=t(f"ai_mode_{mode}")), reply_markup=InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text=t("back"),
                callback_data="config_plugin_bing"
            )
        ]
    ]))
