from pyrogram import filters

from userlixo.assistant.controllers.utils import on_message

on_message(filters.command("start"))
