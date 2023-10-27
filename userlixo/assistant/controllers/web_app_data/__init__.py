from .restart import *
from .save_settings import *
from .upgrade import *


class WebAppDataController:
    @staticmethod
    def register_handlers(client: Client):
        restart.register_handlers(client)
        save_settings.register_handlers(client)
        upgrade.register_handlers(client)
