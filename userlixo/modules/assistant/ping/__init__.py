from userlixo.decorators import controller

from .callback_query import PingCallbackQueryController


@controller(imports=[PingCallbackQueryController])
class PingController:
    pass
