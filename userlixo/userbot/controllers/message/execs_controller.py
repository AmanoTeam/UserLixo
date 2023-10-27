import re
from dataclasses import dataclass

from pyrogram import filters, Client
from pyrogram.types import Message

from userlixo.decorators import Controller, on_message
from userlixo.userbot.handlers.cmd_message_handler import CmdMessageHandler
from userlixo.userbot.handlers.eval_message_handler import EvalMessageHandler
from userlixo.userbot.handlers.exec_message_handler import ExecMessageHandler


@Controller()
@dataclass
class ExecsController:
    cmd_handler: CmdMessageHandler
    eval_handler: EvalMessageHandler
    exec_handler: ExecMessageHandler

    @on_message(filters.su_cmd(r"(?P<command>cmd|sh)\s+(?P<code>.+)", flags=re.S))
    async def cmd(self, client: Client, message: Message):
        await self.cmd_handler.handle_message(client, message)

    @on_message(filters.su_cmd(r"(?P<cmd>ev(al)?)\s+(?P<code>.+)", flags=re.S))
    async def evals(self, client: Client, message: Message):
        await self.eval_handler.handle_message(client, message)

    @on_message(filters.su_cmd(r"(?P<cmd>ex(ec)?)\s+(?P<code>.+)", flags=re.S))
    async def execs(self, client: Client, message: Message):
        await self.exec_handler.handle_message(client, message)
