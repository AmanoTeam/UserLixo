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
        if (m.reply_to_message_id and m.reply_to_message_id in bing_instances):
            bot = bing_instances[m.reply_to_message_id]
            del bing_instances[m.reply_to_message_id]
            mtext = m.text
        else:
            # Check if cookies.json file exists
            if os.path.exists('./cookies.json'):
                # If it exists, open the file and load the cookies
                with open('./cookies.json', 'r', encoding='utf-8') as f:
                    bot = await Chatbot.create(cookies=json.load(f))
            else:
                # If it doesn't exist, create a new Chatbot
                bot = await Chatbot.create()

            # Check if the message is a reply to another message
            if m.reply_to_message:
                mtext = m.reply_to_message.text
                # If the message contains a text, add it to the mtext
                if len(m.text.split(" ", maxsplit=1)) >= 2:
                    mtext = m.text.split(" ", maxsplit=1)[1] + "\n" + f"\"{mtext}\""
            else:
                # If the message is not a reply, get the text after the ".bing" command
                mtext = m.text.split(".bing ", maxsplit=1)[1]

        # Edit the message to show that the bot is searching
        await m.edit(t("ai_bing_searching").format(text=mtext))
        # Ask the bot to search for the mtext
        response = await bot.ask(prompt=mtext, conversation_style=ConversationStyle.creative, simplify_response=True)
        # Get the text from the response
        text = text = f'<pre>{mtext}</pre>\n\n{response["text"]}'
        # Find all the links in the sources_text of the response
        links = re.findall(r'\[(\d+)\.\s(.*?)\]\((.*?)\)',
                           response["sources_text"])
        # Replace the links in the text with HTML links
        for link in links:
            text = text.replace(
                f"[^{link[0]}^]", f'<a href="{link[2]}">[{link[0]}]</a>')

        # Edit the message to show the response
        m = await m.edit(text[:4096], disable_web_page_preview=True)
        
        bing_instances[m.id] = bot
    except Exception as e:
        # If an exception occurs, edit the message to show the exception
        await m.edit(str(e))

# This function is triggered when the ".bingimg" command is sent by a sudoer
@Client.on_message(filters.command("bingimg", prefixes=".") & filters.sudoers)
@use_lang()
async def bingimg(c: Client, m: Message, t):
    # Split the message text into words
    text = m.text.split(" ", maxsplit=1)
    # If the message contains a text, get the text
    if len(text) >= 2:
        text = text[1]
    # If the message is a reply to another message, get the text of the replied message
    elif m.reply_to_message:
        text = m.reply_to_message.text
    else:
        # If the message doesn't contain a text, edit the message to show an error
        return await m.edit(t("ai_no_text"))
    # Edit the message to show that the bot is making the image
    await m.edit(t("ai_making_image").format(text=text))
    # Open the cookies.json file and load the cookies
    with open('./cookies.json', 'r', encoding='utf-8') as f:
        cookies = json.load(f)
    # Get the _U and SRCHHPGUSR cookies
    for cookie in cookies:
        if cookie["name"] == "_U":
            cookie_u = cookie["value"]
        if cookie["name"] == "SRCHHPGUSR":
            cookie_SRCHHPGUSR = cookie["value"]
    # Create an ImageGen object with the cookies
    img_gen = ImageGen(
                        auth_cookie=cookie_u,
                        auth_cookie_SRCHHPGUSR=cookie_SRCHHPGUSR,
                        quiet=True, all_cookies=cookies
                      )
    try:
        # Get the images for the text
        urls = img_gen.get_images(str(text))
    except Exception as e:
        # If an exception occurs, edit the message to show the exception
        return await m.edit(str(e))
    # Create a list of photos from the urls
    photos = []
    for n, i in enumerate(urls):
        photo = io.BytesIO((await http.get(i)).content)
        photos.append(InputMediaPhoto(photo, caption=text if n == 0 else None))
    
    # If the message is a reply to another message, reply to the replied message with the photos
    if m.reply_to_message:
        if m.from_user.is_self:
            await m.delete()
        await m.reply_to_message.reply_media_group(photos)
    else:
        # If the message is not a reply, reply to the message with the photos
        await m.reply_media_group(photos)

# This function is triggered when the ".bard" command is sent by a sudoer
@Client.on_message((filters.command("bard", prefixes=".") | filter_bard) & filters.sudoers)
@use_lang()
async def bardc(c: Client, m: Message, t):
    if (m.reply_to_message_id and m.reply_to_message_id in bard_instances):
        bot = bard_instances[m.reply_to_message_id]
        mtext = m.text
    else:
        session = requests.Session()

        session_cookies = json.load(open("bard_coockies.json", "r"))
        secure_1psid = None

        for cookie in session_cookies:
            session.cookies.set(cookie["name"], 
                                cookie["value"],
                                domain=cookie["domain"],
                                path=cookie["path"])
            if secure_1psid is None and cookie["name"] == "__Secure-1PSID":
                secure_1psid = cookie["value"]
            
        session.headers = {
                        "Host": "bard.google.com",
                        "X-Same-Domain": "1",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) "
                                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                                    "Chrome/91.4472.114 Safari/537.36",
                        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
                        "Origin": "https://bard.google.com",
                        "Referer": "https://bard.google.com/",
                    }

        bot = Bard(session=session, token=secure_1psid)
        
        # Check if the message is a reply to another message
        if m.reply_to_message:
            mtext = m.reply_to_message.text
            # If the message contains a text, add it to the mtext
            if len(m.text.split(" ", maxsplit=1)) >= 2:
                mtext = m.text.split(" ", maxsplit=1)[1] + "\n" + f"\"{mtext}\""
        else:
            # If the message is not a reply, get the text after the ".bing" command
            mtext = m.text.split(" ", maxsplit=1)[1]
    await m.edit(t("ai_bard_searching").format(text=mtext))
    # Get the answer from the chatbard for the mtext
    response = bot.get_answer(mtext)
    text = f'<pre>{mtext}</pre>\n\n{response["content"]}'
    # If the response contains images, create a list of photos from the images and reply to the message with the photos
    if response["images"]:
        photos = []
        for n, i in enumerate(response["images"]):
            photo = io.BytesIO((await http.get(i)).content)
            photos.append(InputMediaPhoto(photo, caption=text[:4096] if n == 0 else None))
        m = await m.reply_media_group(photos)
    else:
        # If the response doesn't contain images, edit the message to show the content of the response
        m = await m.edit(text[:4096])
    bard_instances[m.id] = bot
