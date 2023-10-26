import re

from kink import inject
from pyrogram import filters, Client

from userlixo.assistant.handlers.message.cmd_message_handler import CmdMessageHandler
from userlixo.assistant.handlers.message.eval_message_handler import EvalMessageHandler
from userlixo.assistant.handlers.message.exec_message_handler import ExecMessageHandler
from userlixo.decorators import Controller, on_message


@Controller()
@inject
class ExecsController:
    def __init__(self, cmd_handler: CmdMessageHandler, eval_handler: EvalMessageHandler,
                 exec_handler: ExecMessageHandler):
        self.cmd_handler = cmd_handler
        self.eval_handler = eval_handler
        self.exec_handler = exec_handler

    @on_message(filters.regex(r"^/(?P<command>cmd|sh)\s+(?P<code>.+)", flags=re.S))
    async def cmd_sh(self, client: Client, message):
        await self.cmd_handler.handle_message(client, message)

    @on_message(filters.regex(r"^/(?P<cmd>ex(ec)?)\s+(?P<code>.+)", flags=re.S))
    async def execs(self, client: Client, message):
        await self.exec_handler.handle_message(client, message)

    @on_message(filters.regex(r"^/(?P<cmd>ev(al)?)\s+(?P<code>.+)", flags=re.S))
    async def evals(self, client: Client, message):
        await self.eval_handler.handle_message(client, message)
