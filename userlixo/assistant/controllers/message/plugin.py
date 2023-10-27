from pyrogram import filters, Client

from userlixo.assistant.controllers.utils import on_message


def register_handlers(client: Client):
    on_message(client, filters.document & filters.private & ~filters.me)

    on_message(client, filters.regex("^/(start )?plugin[_ ]add"))

    on_message(client, filters.regex("^/plugins"))
