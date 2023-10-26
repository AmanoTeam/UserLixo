from pyrogram import filters, Client

from userlixo.decorators import Controller, on_message


@Controller()
class RestartController:
    @on_message(filters.regex("^/(start )?restart"))
    def restart(self, client: Client, message):
        pass
