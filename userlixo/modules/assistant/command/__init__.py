from userlixo.decorators import controller

from .callback_query import CommandCallbackQueryController


@controller(imports=[CommandCallbackQueryController])
class CommandController:
    pass
