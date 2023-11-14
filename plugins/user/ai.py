import json
import os
import re

from EdgeGPT.EdgeGPT import Chatbot, ConversationStyle
from pyrogram import Client, filters
from pyrogram.types import Message, InputMediaPhoto
from BingImageCreator import ImageGen
from reload import chatbard
import io
from utils import http


# This function is triggered when the ".bing" command is sent by a sudoer
@Client.on_message(filters.command("bing", prefixes=".") & filters.sudoers)
async def bing(c: Client, m: Message):
    try:
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
        await m.edit(f"Searching {mtext}...")
        # Ask the bot to search for the mtext
        response = await bot.ask(prompt=mtext, conversation_style=ConversationStyle.creative, simplify_response=True)
        # Delete the conversation after getting the response
        await bot.delete_conversation()
        # Close the bot after getting the response
        await bot.close()
        # Get the text from the response
        text = response["text"]
        # Find all the links in the sources_text of the response
        links = re.findall(r'\[(\d+)\.\s(.*?)\]\((.*?)\)',
                           response["sources_text"])
        # Replace the links in the text with HTML links
        for link in links:
            text = text.replace(
                f"[^{link[0]}^]", f'<a href="{link[2]}">[{link[0]}]</a>')

        # Edit the message to show the response
        await m.edit(text[:4096], disable_web_page_preview=True)

        # Close the bot after editing the message
        await bot.close()
    except Exception as e:
        # If an exception occurs, edit the message to show the exception
        await m.edit(str(e))

# This function is triggered when the ".bingimg" command is sent by a sudoer
@Client.on_message(filters.command("bingimg", prefixes=".") & filters.sudoers)
async def bingimg(c: Client, m: Message):
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
        return await m.edit("No text provided")
    # Edit the message to show that the bot is making the image
    await m.edit(f"Making {text}...")
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
@Client.on_message(filters.command("bard", prefixes=".") & filters.sudoers)
async def bardc(c: Client, m: Message):
    # Check if the message is a reply to another message
    if m.reply_to_message:
        mtext = m.reply_to_message.text
        # If the message contains a text, add it to the mtext
        if len(m.text.split(" ", maxsplit=1)) >= 2:
            mtext = m.text.split(" ", maxsplit=1)[1] + "\n" + f"\"{mtext}\""
    # If the message contains a text, get the text after the ".bard" command
    elif len(m.text.split(" ", maxsplit=1)) >= 2:
        mtext = m.text.split(" ", maxsplit=1)[1]
    else:
        # If the message doesn't contain a text, edit the message to show an error
        return await m.edit("No text provided")
    # Edit the message to show that the bot is searching
    await m.edit(f"Searching... {mtext}...")
    print(mtext)
    # Get the answer from the chatbard for the mtext
    response = chatbard.get_answer(mtext)
    print(response)
    # If the response contains images, create a list of photos from the images and reply to the message with the photos
    if response["images"]:
        photos = []
        for n, i in enumerate(response["images"]):
            photo = io.BytesIO((await http.get(i)).content)
            photos.append(InputMediaPhoto(photo, caption=response["content"][:4096] if n == 0 else None))
        await m.reply_media_group(photos)
    else:
        # If the response doesn't contain images, edit the message to show the content of the response
        await m.edit(response["content"][:4096])
