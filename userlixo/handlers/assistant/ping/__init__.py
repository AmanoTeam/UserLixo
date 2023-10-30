from userlixo.decorators import Controller

from .callback_query import PingCallbackQueryController


@Controller(imports=[PingCallbackQueryController])
class PingController:
    pass
