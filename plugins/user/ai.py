import base64
import io
import json
import re
import uuid
from datetime import datetime
from tempfile import NamedTemporaryFile, TemporaryDirectory

import httpx
import markdown
from EdgeGPT.EdgeGPT import Chatbot, ConversationStyle
from gemini import Gemini
from hydrogram import Client, filters
from hydrogram.errors import ListenerTimeout
from hydrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
)
from hydrogram.enums import ChatType
from NewBingImageCreator.aio import ImageCreator
from PIL import Image
from telegraph.aio import Telegraph

from config import bot, plugins
from db import Config
from locales import use_lang
from utils import http

bing_instances = {}
bard_instances = {}
gpt_instances = {}

tones = ["professional", "casual", "polite", "funny", "social+post", "witty"]


async def filter_bing_logic(flt, client: Client, message: Message):
    if message:
        if (
            message.reply_to_message_id
            and message.reply_to_message_id in bing_instances
        ):
            return True
        else:
            return False


filter_bing = filters.create(filter_bing_logic)


async def filter_bard_logic(flt, client: Client, message: Message):
    if message:
        if (
            message.reply_to_message_id
            and message.reply_to_message_id in bard_instances
        ):
            return True
        else:
            return False


filter_bard = filters.create(filter_bard_logic)


async def filter_gpt_logic(flt, client: Client, message: Message):
    if message:
        if message.reply_to_message_id and message.reply_to_message_id in gpt_instances:
            return True
        else:
            return False


filter_gpt = filters.create(filter_gpt_logic)


async def update_page(taccount, path, page_title, page_content, author_info):
    if path:
        oldt = (await taccount.get_page(path))["content"]
        page = await taccount.edit_page(
            path, title=page_title, html_content=oldt + page_content, **author_info
        )
    else:
        page = await taccount.create_page(
            page_title, html_content=page_content, **author_info
        )
    return page


async def process_mode(mtext, mmode):
    if mtext.startswith("-m"):
        mmode = "message"
        mtext = mtext[3:]
    elif mtext.startswith("-t"):
        mmode = "telegraph"
        mtext = mtext[3:]
    elif mtext.startswith("-v"):
        mmode = "voice"
        mtext = mtext[3:]
    elif not mmode:
        mmode = (await Config.get_or_create(id="bard"))[0].value
        if not mmode:
            mmode = "message"
    return mmode, mtext


# This function is triggered when the ".bing" command is sent by a sudoer
@Client.on_message(
    (filters.command(["bing", "copilot"], prefixes=".") | filter_bing) & filters.sudoers
)
@use_lang()
async def bing(c: Client, m: Message, t):
    mmode = None
    try:
        if m.reply_to_message_id and m.reply_to_message_id in bing_instances:
            bot, taccount, path, mmode = bing_instances.pop(m.reply_to_message_id)
            mtext = m.text
        else:
            con = await Config.get_or_none(id="bing")
            if not con:
                return await m.edit(t("ai_not_logged_in"))
            ic = ImageCreator()
            ic.scope = con.valuej["scope"]
            ic.access_token = con.valuej["access_token"]
            ic.vrefresh_token = con.valuej["vrefresh_token"]
            ic.expires_in = datetime.fromtimestamp(con.valuej["expires_in"])
            await ic.get_ms_token()
            await ic.get_ms_cokies()
            con.valuej["expires_in"] = ic.expires_in.timestamp()
            con.valuej["access_token"] = ic.access_token
            await Config.filter(id="bing").update(valuej=json.dumps(con.valuej))
            cookies = ic.copilot_cokies.split("; ")
            cookies = [
                {"name": i.split("=")[0], "value": i.split("=")[1]} for i in cookies
            ]
            bot = Chatbot(cookies=cookies)
            taccount = Telegraph()
            await taccount.create_account(short_name="EdgeGPT")
            path = None
            if m.reply_to_message and m.reply_to_message.text:
                mtext = m.reply_to_message.text
                if len(m.text.split(" ", maxsplit=1)) >= 2:
                    mtext = m.text.split(" ", maxsplit=1)[1] + "\n" + f'"{mtext}"'
            elif m.reply_to_message and m.reply_to_message.caption:
                mtext = m.reply_to_message.caption
                if len(m.text.split(" ", maxsplit=1)) >= 2:
                    mtext = m.text.split(" ", maxsplit=1)[1] + "\n" + f'"{mtext}"'
            elif m.reply_to_message and m.reply_to_message.poll:
                mtext = m.reply_to_message.poll.question + "\n"
                for n, option in enumerate(m.reply_to_message.poll.options):
                    mtext += f"\n{n+1}) {option.text}"
                if len(m.text.split(" ", maxsplit=1)) >= 2:
                    mtext = m.text.split(" ", maxsplit=1)[1] + "\n" + f'"{mtext}"'
            else:
                mtext = m.text.split(" ", maxsplit=1)[1]

        mmode, mtext = await process_mode(mtext, mmode)
        await m.edit(
            t("ai_bing_searching").format(text=f"<blockquote>{mtext}</blockquote>")
        )
        style = ConversationStyle.creative
        if await Config.filter(id="bing").exists():
            mode = (await Config.get(id="bing")).value
            style = (
                ConversationStyle.balanced
                if mode == "balanced"
                else ConversationStyle.precise
            )
        response = await bot.ask(
            prompt=mtext, conversation_style=style, simplify_response=True
        )
        links = re.findall(r"\[(\d+)\.\s(.*?)\]\((.*?)\)", response["sources_text"])
        text = response["text"]
        for link in links:
            text = text.replace(
                f"[^{link[0]}^]", f'<a href="{link[2]}">[{link[0]}]</a>'
            )
        ttext = markdown.markdown(response["text"])

        page_content = f"<blockquote>{mtext}</blockquote>\n\n{ttext}"
        page_title = f"EdgeGPT-userlixo-{c.me.first_name}"
        author_info = {"author_name": "EdgeGPT", "author_url": "https://t.me/UserLixo"}

        page = await update_page(taccount, path, page_title, page_content, author_info)

        if len(text) > 4096 or mmode == "telegraph":
            newm = await m.edit(f'<blockquote>{mtext}</blockquote>\n\n{page["url"]}')
        else:
            newm = await m.edit(f"<blockquote>{mtext}</blockquote>\n\n{text[:4096]}")

        bing_instances[newm.id] = [bot, taccount, page["path"], mmode]
    except Exception as e:
        await m.edit(str(e))


# This function is triggered when the ".bingimg" command is sent by a sudoer
@Client.on_message(
    filters.command(["bingimg", "mkimg"], prefixes=".") & filters.sudoers
)
@use_lang()
async def bingimg(c: Client, m: Message, t):
    text = (
        m.text.split(" ", maxsplit=1)[1]
        if len(m.text.split(" ", maxsplit=1)) >= 2
        else m.reply_to_message.text
        if m.reply_to_message
        else None
    )
    if not text:
        return await m.edit(t("ai_no_text"))

    await m.edit(t("ai_making_image").format(text=text))

    con = await Config.get_or_none(id="bing")
    if not con:
        return await m.edit(t("ai_not_logged_in"))
    ic = ImageCreator()
    ic.scope = con.valuej["scope"]
    ic.access_token = con.valuej["access_token"]
    ic.vrefresh_token = con.valuej["vrefresh_token"]
    ic.expires_in = datetime.fromtimestamp(con.valuej["expires_in"])
    await ic.get_ms_token()
    await ic.get_ms_cokies()
    con.valuej["expires_in"] = ic.expires_in.timestamp()
    con.valuej["access_token"] = ic.access_token
    await Config.filter(id="bing").update(valuej=json.dumps(con.valuej))
    urls = await ic.gen_image(text, "PT", False)

    if "error" in urls:
        error_desc = urls["error"]["message"].split(";")[1]
        error_desc = error_desc.split("=")[1]
        return await m.edit(t("ai_error").format(error=error_desc))

    photos = []

    for n, url in enumerate(urls["images"]):
        x = await http.get(url["thumbnailUrl"])
        photos.append(
            InputMediaPhoto(io.BytesIO(x.content), caption=text if n == 0 else None)
        )

    if m.reply_to_message:
        await m.reply_to_message.reply_media_group(photos)
    else:
        await m.reply_media_group(photos)

    if m.from_user.is_self:
        await m.delete()


# This function is triggered when the ".bingsticker" command is sent by a sudoer
@Client.on_message(
    filters.command(["bingsticker", "mkstr"], prefixes=".") & filters.sudoers
)
@use_lang()
async def bingstr(c: Client, m: Message, t):
    text = (
        m.text.split(" ", maxsplit=1)[1]
        if len(m.text.split(" ", maxsplit=1)) >= 2
        else m.reply_to_message.text
        if m.reply_to_message
        else None
    )
    if not text:
        return await m.edit(t("ai_no_text"))

    await m.edit(t("ai_making_image").format(text=text))

    con = await Config.get_or_none(id="bing")
    if not con:
        return await m.edit(t("ai_not_logged_in"))
    ic = ImageCreator()
    ic.scope = con.valuej["scope"]
    ic.access_token = con.valuej["access_token"]
    ic.vrefresh_token = con.valuej["vrefresh_token"]
    ic.expires_in = datetime.fromtimestamp(con.valuej["expires_in"])
    await ic.get_ms_token()
    await ic.get_ms_cokies()
    con.valuej["expires_in"] = ic.expires_in.timestamp()
    con.valuej["access_token"] = ic.access_token
    await Config.filter(id="bing").update(valuej=json.dumps(con.valuej))
    urls = await ic.gen_sticker(text, "PT", True)

    if "error" in urls:
        error_desc = urls["error"]["message"].split(";")[1]
        error_desc = error_desc.split("=")[1]
        return await m.edit(t("ai_error").format(error=error_desc))

    for n, url in enumerate(urls["images"]):
        img_base64 = url["imageBackgroundRemovedBase64"]
        img_bytes = base64.b64decode(img_base64)
        image = Image.open(io.BytesIO(img_bytes))
        with NamedTemporaryFile(suffix=".webp") as f:
            image.save(f.name, "WEBP")
            if m.reply_to_message:
                await m.reply_to_message.reply_sticker(f.name)
            else:
                await m.reply_sticker(f.name)


@Client.on_message(filters.command("tone", prefixes=".") & filters.sudoers)
@bot.on_callback_query(filters.regex(r"^ai_tone_") & filters.sudoers)
@use_lang()
async def tone(c: Client, m: Message | CallbackQuery, t):
    if isinstance(m, Message):
        text = (
            m.text.split(" ", maxsplit=1)[1]
            if len(m.text.split(" ", maxsplit=1)) >= 2
            else m.reply_to_message.text
            if m.reply_to_message
            else None
        )
        if not text:
            return await m.edit(t("ai_no_text"))

    con = await Config.get_or_none(id="tone")
    if isinstance(m, Message) and (not con or con.valuej["type"] == "quest"):
        await Config.get_or_create(id="tone")
        await Config.filter(id="tone").update(valuej={"type": "quest"}, value=text)
        kb = [
            [InlineKeyboardButton(text=t(tone), callback_data=f"ai_tone_{tone}")]
            for tone in tones
        ]
        if m.from_user.is_self:
            await m.delete()
        return await m.reply(t("chose_tone"), reply_markup=InlineKeyboardMarkup(kb))

    if isinstance(m, CallbackQuery):
        text = con.value
        tone = m.data.split("_")[-1]
    else:
        tone = con.valuej["type"]

    await m.edit(t("ai_making_text").format(text=text, tone=t(tone)))
    con = await Config.get_or_none(id="bing")
    if not con:
        return await m.edit(t("ai_not_logged_in"))
    ic = ImageCreator()
    ic.scope = con.valuej["scope"]
    ic.access_token = con.valuej["access_token"]
    ic.vrefresh_token = con.valuej["vrefresh_token"]
    ic.expires_in = datetime.fromtimestamp(con.valuej["expires_in"])
    await ic.get_ms_token()
    await ic.get_ms_cokies()
    con.valuej["expires_in"] = ic.expires_in.timestamp()
    con.valuej["access_token"] = ic.access_token
    await Config.filter(id="bing").update(valuej=json.dumps(con.valuej))

    rtext = await ic.tone_rewrite(text)

    if "error" in rtext:
        error_desc = rtext["error"]["message"].split(";")[1]
        error_desc = error_desc.split("=")[1]
        return await m.edit(t("ai_error").format(error=error_desc))

    await m.edit(rtext["tones"][tone.replace("+", " ")])


@Client.on_message(
    (filters.command("gpt", prefixes=".") | filter_gpt) & filters.sudoers
)
@use_lang()
async def gpt(c: Client, m: Message, t):
    await m.edit(t("wait"))
    if m.reply_to_message_id and m.reply_to_message_id in gpt_instances:
        form = gpt_instances.pop(m.reply_to_message_id)
        mtext = m.text
        form.append(
            dict(
                role="user",
                content=[{"type": "text", "text": m.text}],
                name=m.from_user.first_name,
            )
        )
    else:
        mtext = m.text.split(" ", maxsplit=1)
        if len(mtext) >= 2:
            mtext = mtext[1]
            form = [
                dict(
                    role="user",
                    content=[{"type": "text", "text": mtext}],
                    name=m.from_user.first_name,
                )
            ]
        else:
            mtext = m.reply_to_message.text
            form = []
        mes = m.reply_to_message if m.reply_to_message else None
        if mes:
            for _ in range(10):
                print(mes)
                if mes.photo or mes.sticker:
                    content = []
                    taccount = Telegraph()
                    await taccount.create_account(short_name="GPT-4o")
                    with TemporaryDirectory() as tempdir:
                        photo = await c.download_media(
                            mes, file_name=tempdir, in_memory=True
                        )
                        encoded_string = base64.b64encode(photo.getvalue()).decode(
                            "utf-8"
                        )
                    content.append(
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_string}"
                            },
                        }
                    )
                    if mes.caption:
                        content.append({"type": "text", "text": mes.caption})
                    else:
                        content.append({"type": "text", "text": "Photo"})
                else:
                    content = mes.text
                form.append(
                    dict(
                        role="user",
                        content=content,
                        name=mes.from_user.first_name,
                    )
                )
                if mes.reply_to_message_id:
                    mes = await c.get_messages(m.chat.id, mes.reply_to_message_id)
                else:
                    break

        form.append(
            {
                "role": "system",
                "content": f"You are an open source user bot called UserLixo that was developed by amanoteam, {c.me.first_name} is running it on "
                + (
                    f"a private chat with {m.chat.first_name}"
                    if m.chat.type == ChatType.PRIVATE
                    else f"a group with name {m.chat.title}"
                ),
            }
        )
        form = form[::-1]

    headers = {
        "Content-Type": "application/json",
        "x-device-id": str(uuid.uuid4()),
    }

    payload = {
        "messages": form,
        "model": "gpt-4o",
        "stream": False,
    }


    async with httpx.AsyncClient() as httpx_client:
        response = await httpx_client.post(
            "https://api.amigochat.io/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=340,
        )

    if response.status_code != 201:
        return await m.edit(response.text)
    else:
        rtext = response.json()["message"]["choices"][0]["message"]["content"]
        text = f"<blockquote>{mtext}</blockquote>\n\n{rtext}"
        await m.edit(text)

        form.append(
            dict(
                role="assistant",
                content=rtext,
            )
        )

        gpt_instances[m.id] = form


@Client.on_message(
    (filters.command(["bard", "gemini"], prefixes=".") | filter_bard) & filters.sudoers
)
@use_lang()
async def bardc(c: Client, m: Message, t):
    teleimg = None
    mmode = None
    try:
        cookies = json.load(open("bard_coockies.json", "r"))
        cookies = {cookie["name"]: cookie["value"] for cookie in cookies}
        if m.reply_to_message_id and m.reply_to_message_id in bard_instances:
            olbot, taccount, path, mmode = bard_instances.pop(m.reply_to_message_id)
            bot = Gemini(cookies=cookies)
            bot._sid = olbot._sid
            bot._rcid = olbot._rcid
            bot._rid = olbot._rid
            bot._cid = olbot._cid
            bot._reqid = olbot._reqid + 100000
            mtext = m.text
        else:
            taccount = Telegraph()
            await taccount.create_account(short_name="Gemini")
            path = None
            bot = Gemini(cookies=cookies)
            if m.reply_to_message and m.reply_to_message.text:
                mtext = m.reply_to_message.text
                if len(m.text.split(" ", maxsplit=1)) >= 2:
                    mtext = m.text.split(" ", maxsplit=1)[1] + "\n" + f'"{mtext}"'
            elif m.reply_to_message and m.reply_to_message.caption:
                mtext = m.reply_to_message.caption
                if len(m.text.split(" ", maxsplit=1)) >= 2:
                    mtext = m.text.split(" ", maxsplit=1)[1] + "\n" + f'"{mtext}"'
            elif m.reply_to_message and m.reply_to_message.poll:
                mtext = m.reply_to_message.poll.question + "\n"
                for n, option in enumerate(m.reply_to_message.poll.options):
                    mtext += f"\n{n+1}) {option.text}"
                if len(m.text.split(" ", maxsplit=1)) >= 2:
                    mtext = m.text.split(" ", maxsplit=1)[1] + "\n" + f'"{mtext}"'
            else:
                mtext = m.text.split(" ", maxsplit=1)[1]

        mmode, mtext = await process_mode(mtext, mmode)
        await m.edit(
            t("ai_bard_searching").format(text=f"<blockquote>{mtext}</blockquote>")
        )
        if m.reply_to_message and (
            m.reply_to_message.photo or m.reply_to_message.sticker
        ):
            file = await c.download_media(m.reply_to_message, in_memory=True)
            file_bytes = bytes(file.getbuffer())
            try:
                with NamedTemporaryFile() as f:
                    f.write(file_bytes)
                    teleimg = await taccount.upload_file(f.name)
            except:
                pass
        else:
            file_bytes = None
        response = bot.generate_content(mtext, image=file_bytes)
        text = f"<blockquote>{mtext}</blockquote>\n\n{response.text}"

        ttext = markdown.markdown(response.text)
        for i in response.web_images:
            ttext = ttext.replace(i.title, f"<img src='{str(i.url)}'>")

        page_content = (
            f"<img src='https://telegra.ph{teleimg[0]['src']}'><br>\n\n"
            if teleimg
            else ""
        )
        page_content += f"<blockquote>{mtext}</blockquote>\n\n{ttext}"
        page_title = f"Gemini-userlixo-{c.me.first_name}"
        author_info = {"author_name": "Gemini", "author_url": "https://t.me/UserLixo"}

        page_content = re.sub(r"<h\d.*?>(.*?)</h\d>", r"<h3>\1</h3>", page_content)
        page_content = re.sub(r"<b>(.*?)</p>", r"<b>\1</b>", page_content)
        page = await update_page(taccount, path, page_title, page_content, author_info)
        if len(text) > 4096 or mmode == "telegraph":
            newm = await m.edit(f'<blockquote>{mtext}</blockquote>\n\n{page["url"]}')
        elif mmode == "voice":
            audio = bot.speech(response.text)
            with NamedTemporaryFile(suffix=".mp3") as f:
                f.write(bytes(audio["audio"]))
                newm = await m.reply_voice(
                    f.name, caption=f'<blockquote>{mtext}</blockquote>\n\n{page["url"]}'
                )
        elif response.web_images:
            photos = [
                InputMediaPhoto(str(i.url), caption=text[:4096] if n == 0 else None)
                for n, i in enumerate(response.web_images)
            ]
            newm = (await m.reply_media_group(photos))[0]
        else:
            newm = await m.edit(text[:4096])

        bard_instances[newm.id] = [bot, taccount, page["path"], mmode]
    except Exception as e:
        await m.edit(str(e))


plugins.append("bing")


@bot.on_callback_query(filters.regex(r"\bconfig_plugin_bing\b"))
@use_lang()
async def config_bing(c: Client, cq: CallbackQuery, t):
    await cq.edit_message_text(
        t("bing_settings"),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=t("ai_mode"), callback_data="config_plugin_ai_mode"
                    ),
                    InlineKeyboardButton(
                        text=t("ai_login"),
                        callback_data="config_plugin_bing_login",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=t("tone_config"),
                        callback_data="config_plugin_bing_tone",
                    ),
                    InlineKeyboardButton(
                        text=t("back"), callback_data="config_plugins"
                    ),
                ],
            ]
        ),
    )


@bot.on_callback_query(filters.regex(r"\bconfig_plugin_ai_mode\b"))
@use_lang()
async def config_ai_mode(c: Client, cq: CallbackQuery, t):
    await cq.edit(
        t("ai_mode_choose"),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=t("ai_mode_creative"),
                        callback_data="config_plugin_ai_mode_creative",
                    ),
                    InlineKeyboardButton(
                        text=t("ai_mode_balanced"),
                        callback_data="config_plugin_ai_mode_balanced",
                    ),
                    InlineKeyboardButton(
                        text=t("ai_mode_precise"),
                        callback_data="config_plugin_ai_mode_precise",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=t("back"), callback_data="config_plugin_bing"
                    )
                ],
            ]
        ),
    )


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
    await cq.edit(
        t("ai_mode_changed").format(style=t(f"ai_mode_{mode}")),
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=t("back"), callback_data="config_plugin_bing")]]
        ),
    )


@bot.on_callback_query(filters.regex(r"\bconfig_plugin_bing_login\b"))
@use_lang()
async def config_bing_login(c: Client, cq: CallbackQuery, t):
    login_url = ImageCreator().login_url
    kb = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text=t("ai_login"), url=login_url),
            ],
            [InlineKeyboardButton(text=t("back"), callback_data="config_plugin_bing")],
        ]
    )
    await cq.edit(t("ai_login_text"), reply_markup=kb)
    cmessage = None

    while cmessage is None:
        try:
            cmessage = await cq.message.chat.listen(filters.text & filters.sudoers)
        except ListenerTimeout:
            return

    if cmessage.text.startswith("https://login.live.com/oauth20_desktop"):
        code = cmessage.text.split("?code=")[1].split("&")[0]
        ic = ImageCreator()
        await ic.login(code)
        cookies = dict(
            scope=ic.scope,
            access_token=ic.access_token,
            vrefresh_token=ic.vrefresh_token,
            expires_in=ic.expires_in.timestamp(),
        )
        await Config.get_or_create(id="bing")
        await Config.filter(id="bing").update(valuej=json.dumps(cookies))
        kb = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=t("back"), callback_data="config_plugin_bing"
                    ),
                ],
            ]
        )
        await cq.edit(t("ai_login_success"))


@bot.on_callback_query(filters.regex(r"\bconfig_plugin_bing_tone\b"))
@use_lang()
async def config_bing_tone(c: Client, cq: CallbackQuery, t):
    kb = [
        [
            InlineKeyboardButton(
                text=t(tone), callback_data=f"config_plugin_bing_tone_{tone}"
            )
        ]
        for tone in tones
    ]
    kb.append(
        [
            InlineKeyboardButton(
                text=t("quest"), callback_data="config_plugin_bing_tone_quest"
            )
        ]
    )
    kb.append(
        [InlineKeyboardButton(text=t("back"), callback_data="config_plugin_bing")]
    )

    await cq.edit(t("chose_tone"), reply_markup=InlineKeyboardMarkup(kb))


@bot.on_callback_query(filters.regex(r"\bconfig_plugin_bing_tone_"))
@use_lang()
async def config_bing_tones(c: Client, cq: CallbackQuery, t):
    tone = cq.data.split("_")[-1]
    await Config.get_or_create(id="tone")
    await Config.filter(id="tone").update(valuej={"type": tone})
    await cq.edit(
        t("tone_set").format(tone=t(tone)),
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=t("back"), callback_data="config_plugin_bing")]]
        ),
    )


plugins.append("bard")


@bot.on_callback_query(filters.regex(r"\bconfig_plugin_bard\b"))
@use_lang()
async def config_bard(c: Client, cq: CallbackQuery, t):
    await cq.edit(
        t("bard_settings"),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=t("bard_ai_mode"), callback_data="config_plugin_bard_mode"
                    )
                ],
                [InlineKeyboardButton(text=t("back"), callback_data="config_plugins")],
            ]
        ),
    )


@bot.on_callback_query(filters.regex(r"\bconfig_plugin_bard_mode\b"))
@use_lang()
async def config_bard_mode(c: Client, cq: CallbackQuery, t):
    bc = await Config.get_or_create(id="bard")
    if bc[0].value:
        mode = bc[0].value
    else:
        mode = "message"
    await cq.edit(
        t("ai_mode_choose"),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=t(f"ai_mode_{mode}"),
                        callback_data="config_plugin_bard_mode_toggle",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=t("back"), callback_data="config_plugin_bard"
                    )
                ],
            ]
        ),
    )


@bot.on_callback_query(filters.regex(r"\bconfig_plugin_bard_mode_toggle\b"))
@use_lang()
async def config_bard_mode_toggle(c: Client, cq: CallbackQuery, t):
    bc = await Config.get(id="bard")
    if bc.value:
        mode = bc.value
    else:
        mode = "message"
    modes = ["message", "telegraph", "voice"]
    mode = modes[(modes.index(mode) + 1) % len(modes)]

    await Config.filter(id="bard").update(value=mode)
    await cq.edit(
        t("ai_mode_choose"),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=t(f"ai_mode_{mode}"),
                        callback_data="config_plugin_bard_mode_toggle",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=t("back"), callback_data="config_plugin_bard"
                    )
                ],
            ]
        ),
    )
