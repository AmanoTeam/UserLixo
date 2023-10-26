import re

from pyrogram import filters, Client

from userlixo.decorators import Controller, on_message


@Controller()
class ExecsController:
    @on_message(filters.regex(r"^/(?P<command>cmd|sh)\s+(?P<code>.+)", flags=re.S))
    def cmd_sh(self, client: Client, message):
        pass

    @on_message(filters.regex(r"^/(?P<cmd>ev(al)?)\s+(?P<code>.+)", flags=re.S))
    def eval(self, client: Client, message):
        pass

    @on_message(filters.regex(r"^/(?P<cmd>ex(ec)?)\s+(?P<code>.+)", flags=re.S))
    def exec(self, client: Client, message):
        pass
