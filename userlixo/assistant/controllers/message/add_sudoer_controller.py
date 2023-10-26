from pyrogram import filters, Client

from userlixo.decorators import Controller, on_message


@Controller()
class AddSudoerController:
    @on_message(filters.regex("^/(start )?add_sudoer"))
    def add_sudoer(self, client: Client, message):
        pass
