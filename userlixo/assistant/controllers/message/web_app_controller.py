from pyrogram import filters, Client

from userlixo.decorators import Controller, on_message


@Controller()
class WebAppController:
    @on_message(filters.regex("^/(start )?webapp"))
    def webapp(self, client: Client, message):
        pass
