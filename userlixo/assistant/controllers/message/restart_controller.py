from pyrogram import filters, Client

from userlixo.decorators import Controller, on_message


@Controller()
class RestartController:
    @staticmethod
    @on_message(filters.regex("^/(start )?restart"))
    def restart(client: Client, message):
        pass
