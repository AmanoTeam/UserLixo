from pyrogram import filters, Client

from userlixo.decorators import Controller, on_message


@Controller()
class WebAppController:
    @staticmethod
    @on_message(filters.regex("^/(start )?webapp"))
    def webapp(client: Client, message):
        pass
