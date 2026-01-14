import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Union

from hydrogram import Client, filters
from hydrogram.enums import MessageEntityType, UserStatus
from hydrogram.helpers import ikb
from hydrogram.types import CallbackQuery, Message

from config import bot
from db import Config
from locales import use_lang
from utils import http


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
        await m.edit(t("online").format(mention=usr.mention))
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
    await Config.update_or_create(
        id="restart",
        defaults={"valuej": {"chat_id": msg.chat.id, "message_id": msg.id}},
    )
    os.execl(sys.executable, sys.executable, *sys.argv)


@Client.on_message(filters.command("save", prefixes=".") & filters.sudoers)
@use_lang()
async def save(c: Client, m: Message, t):
    msg = await m.edit(t("saving"))
    x = await m.reply_to_message.forward(bot.me.id)
    print(x)
    await bot.forward_messages(
        chat_id=m.from_user.id, from_chat_id=c.me.id, message_ids=x.id
    )
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
    text = ""
    async for user in c.get_chat_members(m.chat.id):
        if user.user.is_bot:
            continue
        text += f"{user.user.mention}\n"

    await m.reply_text(text)


@Client.on_message(filters.command("mcserver", prefixes=".") & filters.sudoers)
@bot.on_callback_query(filters.regex("^mcserver ") & filters.sudoers)
@use_lang()
async def mcserver(c: Client, m: Union[Message, CallbackQuery], t):
    if isinstance(m, CallbackQuery):
        fun = m.edit_message_text
        ip = m.data.split(" ")[1]
    elif isinstance(m, Message):
        fun = m.reply
        ip = m.text.split(" ", 1)[1]

    r = await http.get(f"https://api.mcstatus.io/v2/status/java/{ip}")
    java = r.json()

    r = await http.get(f"https://api.mcstatus.io/v2/status/bedrock/{ip}")
    bedrock = r.json()

    pre_keyb = []
    if java["online"] and "mods" in java and len(java["mods"]) > 0:
        pre_keyb.append(("Mods (java)", f"mcservermods {ip} 0"))
    if (
        java["online"]
        and "list" in java["players"]
        and len(java["players"]["list"]) > 0
    ):
        pre_keyb.append(("Players (java)", f"mcserverplayers {ip}"))

    keyb = [[("🔄 " + t("refresh"), f"mcserver {ip}")]] + [pre_keyb]

    txt = ""

    if java["online"]:
        txt += f"""<b>STATUS SERVER JAVA:</b>
    IP: {java["host"] if "host" in java else java["ip_address"]} (<code>{java["ip_address"]}</code>)
    <b>Port:</b> <code>{java["port"]}</code>
    <b>Online:</b> <code>{"✅" if java["online"] else "✖️"}</code>
    <b>Mods:</b> <code>{len(java["mods"]) if "mods" in java else "N/A"}</code>
    <b>Players:</b> <code>{java["players"]["online"]}/{java["players"]["max"]}</code>
    <b>Version:</b> <code>{java["version"]["name_clean"]}</code>
    <b>MOTD:</b> {java["motd"]["clean"]}\n\n"""
        txt += (
            f"Updated at: <code>{datetime.fromtimestamp(java['retrieved_at'] / 1000)}</code>\n"
            ""
        )
        txt += f"Next update in: <code>{datetime.fromtimestamp(java['expires_at'] / 1000)}</code>\n\n"
    if bedrock["online"]:
        txt += f"""<b>STATUS SERVER BEDROCK:</b>
    IP: {bedrock["host"] if "host" in bedrock else bedrock["ip_address"]} (<code>{bedrock["ip_address"]}</code>)
    <b>Port:</b> <code>{bedrock["port"]}</code>
    <b>Online:</b> <code>{"✅" if bedrock["online"] else "✖️"}</code>
    <b>Players:</b> <code>{bedrock["players"]["online"]}/{bedrock["players"]["max"]}</code>
    <b>Version:</b> <code>{bedrock["version"]["name"]}</code>
    <b>MOTD:</b> {bedrock["motd"]["clean"]}\n\n"""
        txt += f"Updated at: <code>{datetime.fromtimestamp(bedrock['retrieved_at'] / 1000)}</code>\n"
        txt += f"Next update in: <code>{datetime.fromtimestamp(bedrock['expires_at'] / 1000)}</code>\n\n"
    if txt == "":
        txt += f"""<b>STATUS SERVER:</b>
    <b>IP:</b> {java["host"] if "host" in java else java["ip_address"]} (<code>{java["ip_address"]}</code>)
    <b>Port:</b> <code>{java["port"]}</code>
    <b>Online:</b> <code>{"✅" if java["online"] else "✖️"}</code>"""

    await fun(txt, reply_markup=ikb(keyb))


@bot.on_callback_query(filters.regex("^mcservermods ") & filters.sudoers)
@use_lang()
async def mcservermods(c: Client, m: CallbackQuery, t):
    ip, page = m.data.split(" ")[1:]
    r = await http.get(f"https://api.mcstatus.io/v2/status/java/{ip}")
    a = r.json()
    keyb_page = []
    total_pages = len(a["mods"]) // 10
    if len(a["mods"]) % 10 != 0:
        total_pages += 1
    if int(page) != 0:
        keyb_page.append(("⬅️", f"mcservermods {ip} {int(page) - 1}"))
    if int(page) != total_pages - 1:
        keyb_page.append(("➡️", f"mcservermods {ip} {int(page) + 1}"))

    keyb = [[(t("back"), f"mcserver {ip}")]] + [keyb_page]
    print(keyb)

    if a["online"]:
        txt = f"<b>Mods from server {a['host'] if 'host' in a else a['ip_address']}:{a['port']}</b>\n\n"
        if "mods" in a:
            for i in range(int(page) * 10, int(page) * 10 + 10):
                try:
                    txt += f"• <code>{a['mods'][i]['name']}</code> - {a['mods'][i]['version']}\n"
                except IndexError:
                    break
            txt += f"\n\n--- Page {int(page) + 1}/{total_pages} ---"
    else:
        txt = f"""<b>STATUS SERVER:</b>
    <b>IP:</b> {a["host"] if "host" in a else a["ip_address"]} (<code>{a["ip_address"]}</code>)
    <b>Port:</b> <code>{a["port"]}</code>
    <b>Online:</b> <code>{"✅" if a["online"] else "✖️"}</code>"""

    await m.edit_message_text(txt, reply_markup=ikb(keyb))


@bot.on_callback_query(filters.regex("^mcserverplayers ") & filters.sudoers)
@use_lang()
async def mcserverplayers(c: Client, m: CallbackQuery, t):
    ip = m.data.split(" ")[1]
    r = await http.get(f"https://api.mcstatus.io/v2/status/java/{ip}")
    a = r.json()

    keyb = [[(t("back"), f"mcserver {ip}")]]

    if a["online"]:
        txt = f"<b>Players from server {a['host'] if 'host' in a else a['ip_address']}:{a['port']}</b>\n\n"
        if "list" in a["players"]:
            for i in a["players"]["list"]:
                txt += f"• {i['name_clean']}\n"
    else:
        txt = f"""<b>STATUS SERVER:</b>
    <b>IP:</b> {a["host"] if "host" in a else a["ip_address"]} (<code>{a["ip_address"]}</code>)
    <b>Port:</b> <code>{a["port"]}</code>
    <b>Online:</b> <code>{"✅" if a["online"] else "✖️"}</code>"""

    await m.edit_message_text(txt, reply_markup=ikb(keyb))
