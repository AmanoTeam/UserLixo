import re
from dataclasses import dataclass

from pyrogram import filters, Client
from pyrogram.types import Message

from userlixo.decorators import Controller, on_message
from userlixo.userbot.handlers.cmd_message_handler import CmdMessageHandler


@Controller()
@dataclass
class CmdController:
    handler: CmdMessageHandler

    @on_message(filters.su_cmd(r"(?P<command>cmd|sh)\s+(?P<code>.+)", flags=re.S))
    async def cmd(self, client: Client, message: Message):
        await self.handler.handle_message(client, message)
