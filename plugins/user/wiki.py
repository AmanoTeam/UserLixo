from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from locales import use_lang
import desciclopedia
import wikipedia
from db import Config, Message
from config import bot

@Client.on_message(filters.command("wiki", prefixes=".") & filters.sudoers)
@use_lang()
async def wiki(c: Client, m: Message, t):
    txt = m.text.split(" ", 1)[1]
    lang = await Config.get_or_none(id="wikilang")
    lang = lang.value if lang else "pt"
    wik = wikipedia.search(txt)
    wikipedia.set_lang(lang)
    
    if wik:
        mes = await Message.create(text=txt, keyboard=wik)
        ter = [(a, f"wiki_{i}_{mes.key}") for i, a in enumerate(wik)]
        it = iter(ter)
        keyb = [[x, next(it)] for x in it]
        await m.reply(t("wiki_choose"), reply_markup=keyb)
    else:
        await m.edit(t("wiki_no_results").format(query=txt))

@Client.on_message(filters.command("dwiki", prefixes=".") & filters.sudoers)
@use_lang()
async def dwiki(c: Client, m: Message, t):
    txt = m.text.split(" ", 1)[1]
    print(txt)
    wik = desciclopedia.search(txt)
    if wik:
        mes = await Message.create(text=txt, keyboard=wik)
        ter = [(a, f"dwiki_{i}_{mes.key}") for i, a in enumerate(wik)]
        it = iter(ter)
        keyb = [[x, next(it)] for x in it]
        await m.reply(t("wiki_choose"), reply_markup=keyb)
    else:
        await m.edit(t("wiki_no_results").format(query=txt))

@bot.on_callback_query(filters.regex(r"^wiki_") & filters.sudoers)
@use_lang()
async def wiki_cq(_, cq, t):
    num, index = cq.data.split("_", 2)[1:]
    num = int(num)
    mes = await Message.get_or_none(key=index)
    if not mes:
        return await cq.answer(t("old_msg"))
    try:
        wik = wikipedia.page(mes.keyboard[num])
    except:
        return await cq.answer(t("wiki_error"))
    await cq.edit(
        wik.content[:2096],
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(t("read_more"), url=wik.url)]
            ]
        ),
    )
    await (await Message.get(key=mes.key)).delete()

@bot.on_callback_query(filters.regex(r"^dwiki_") & filters.sudoers)
@use_lang()
async def dwiki_cq(_, cq, t):
    num, index = cq.data.split("_", 2)[1:]
    num = int(num)
    mes = await Message.get_or_none(key=index)
    if not mes:
        return await cq.answer(t("old_msg"))
    try:
        wik = desciclopedia.page(mes.keyboard[num])
    except:
        return await cq.answer(t("wiki_error"))
    await cq.edit(
        wik.content[:2096],
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(t("read_more"), url=wik.url)]
            ]
        ),
    )
    await (await Message.get(key=mes.key)).delete()