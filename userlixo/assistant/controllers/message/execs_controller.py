import re

from pyrogram import filters, Client

from userlixo.decorators import Controller, on_message


@Controller()
class ExecsController:
    @staticmethod
    @on_message(filters.regex(r"^/(?P<command>cmd|sh)\s+(?P<code>.+)", flags=re.S))
    def cmd_sh(client: Client, message):
        pass

    @staticmethod
    @on_message(filters.regex(r"^/(?P<cmd>ev(al)?)\s+(?P<code>.+)", flags=re.S))
    def eval(client: Client, message):
        pass

    @staticmethod
    @on_message(filters.regex(r"^/(?P<cmd>ex(ec)?)\s+(?P<code>.+)", flags=re.S))
    def exec(client: Client, message):
        pass
