from pyrogram import filters

from userlixo.assistant.controllers.utils import on_message

on_message(filters.document & filters.private & ~filters.me)

on_message(filters.regex("^/(start )?plugin[_ ]add"))

on_message(filters.regex("^/plugins"))
