from pyrogram import filters, Client

from userlixo.decorators import Controller, on_message


@Controller()
class SaveSettingsController:
    @staticmethod
    @on_message(filters.web_data_cmd("save_settings"))
    def save_settings(self, client: Client, message):
        pass
