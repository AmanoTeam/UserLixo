from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from pyrogram.helpers import ikb
from locales import use_lang
from pyrogram.enums import UserStatus, MessageEntityType
from datetime import datetime
from pathlib import Path
from db import Config
from config import bot
import os
import sys
import asyncio
from utils import http
from typing import Union
from datetime import datetime

@Client.on_message(filters.command("on", prefixes=".") & filters.sudoers)
@use_lang()
async def on(c: Client, m: Message, t):
    if m.reply_to_message:
        user_id = m.reply_to_message.from_user.id
    elif m.entities and m.entities[0].type == MessageEntityType.TEXT_MENTION:
        user_id = m.entities[0].user.id
    # User ids: integers
    elif m.command[1].isdigit():
        user_id = int(m.command[1])
    # Usernames and phone numbers with +
    else:
        user_id = m.command[1]
    usr = await c.get_users(user_id)
    if usr.is_bot:
        await m.edit(t("not_bot"))
    elif usr.is_deleted:
        await m.edit(t("deleted"))
    elif usr.status == UserStatus.ONLINE:
        await m.edit(
            t("online").format(mention=usr.mention)
        )
    elif not usr.last_online_date:
        await m.edit(t("no_data"))
    else:
        c = datetime.now() - usr.last_online_date
        frase = t("offline").format(mention=usr.mention)
        days = c.days
        years = days // 365
        months = (days % 365) // 30
        days = days % 30
        if years != 0:
            frase += t("years").format(years=years)
        if months != 0:
            frase += t("months").format(months=months)
        if days != 0:
            frase += t("days").format(days=days)
        if c.seconds // 3600 != 0:
            frase += t("hours").format(hours=c.seconds // 3600)
        if (c.seconds // 60) % 60 != 0:
            frase += t("minutes").format(minutes=(c.seconds // 60) % 60)
        if c.seconds % 60 != 0:
            frase += t("seconds").format(seconds=c.seconds % 60)
        await m.edit(frase)

@Client.on_message(filters.command("ping", prefixes=".") & filters.sudoers)
@use_lang()
async def ping(c: Client, m: Message, t):
    t1 = datetime.now()
    msg = await m.edit("Pong!")
    t2 = datetime.now()
    await msg.edit(f"**Pong!** `{(t2 - t1).microseconds / 1000}`ms")

@Client.on_message(filters.command("doc", prefixes=".") & filters.sudoers)
@use_lang()
async def doc(c: Client, m: Message, t):
    file = m.text.split(" ", 1)[1]
    if not Path(file).exists():
        await m.edit(t("no_file"))
        return
    else:
        await m.reply_document(file)

@Client.on_message(filters.command("restart", prefixes=".") & filters.sudoers)
@use_lang()
async def restart(c: Client, m: Message, t):
    msg: Message = await m.edit(t("restarting"))
    print(msg)
    await Config.update_or_create(id="restart", defaults={"valuej": {"chat_id": msg.chat.id, "message_id": msg.id}})
    os.execl(sys.executable, sys.executable, *sys.argv)

@Client.on_message(filters.command("save", prefixes=".") & filters.sudoers)
@use_lang()
async def save(c: Client, m: Message, t):
    msg = await m.edit(t("saving"))
    x = await m.reply_to_message.forward(bot.me.id)
    print(x)
    await bot.forward_messages(chat_id=m.from_user.id, from_chat_id=c.me.id, message_ids=x.id)
    await x.delete()
    await msg.edit(t("saved"))

@Client.on_message(filters.command("text", prefixes=".") & filters.sudoers)
@use_lang()
async def text(c: Client, m: Message, t):
    ch = ""
    txt = m.text.split(" ", 1)[1]
    ms = await m.edit("`|`")
    for i in txt:
        ch += i
        ms = await ms.edit(f"`{ch}|`")
        await asyncio.sleep(0.1)
        ms = await ms.edit(f"`{ch.strip()}`")
        await asyncio.sleep(0.1)

@Client.on_message(filters.command("tagall", prefixes=".") & filters.sudoers)
@use_lang()
async def tagall(c: Client, m: Message, t):
    users = await c.get_chat_members(m.chat.id)
    text = ""
    for user in users:
        if user.user.is_bot:
            continue
        text += f"{user.mention}\n"
    
    await m.reply_text(text)

@Client.on_message(filters.command("mcserver", prefixes=".") & filters.sudoers)
@bot.on_callback_query(filters.regex("^mcserver") & filters.sudoers)
@use_lang()
async def mcserver(c: Client, m: Union[Message, CallbackQuery], t):
    if isinstance(m, CallbackQuery):
        fun = m.edit_message_text
        ip = m.data.split(" ")[1]
    elif isinstance(m, Message):
        fun = m.reply
        ip = m.text.split(" ", 1)[1]
    
    r = await http.get(f"https://api.mcsrvstat.us/2/{ip}")
    a = r.json()
    
    keyb = [[("🔄 " + t("refresh"), f"mcserver {ip}")]]
    
    if a["online"]:
        txt = f"""<b>STATUS SERVER:</b>
    IP: {a['hostname'] if 'hostname' in a else a['ip']} (<code>{a['ip']}</code>)
    <b>Port:</b> <code>{a['port']}</code>
    <b>Online:</b> <code>{a['online']}</code>
    <b>Mods:</b> <code>{len(a['mods']['names']) if 'mods' in a else 'N/A'}</code>
    <b>Players:</b> <code>{a['players']['online']}/{a['players']['max']}</code>
    <b>Version:</b> <code>{a['version']}</code>
    <b>MOTD:</b> {a['motd']['html'][0]}\n\n"""
        txt += f"Updated at: <code>{datetime.fromtimestamp(a['debug']['cachetime']-10800)}</code>\n"""
        txt += f"Next update in: <code>{datetime.fromtimestamp(a['debug']['cacheexpire']-10800)}</code>"
    else:
        txt = f"""<b>STATUS SERVER:</b>
    <b>IP:</b> {a['hostname'] if 'hostname' in a else a['ip']} (<code>{a['ip']}</code>)
    <b>Port:</b> <code>{a['port']}</code>
    <b>Online:</b> <code>{a['online']}</code>"""
    
    await fun(txt, reply_markup=ikb(keyb))
