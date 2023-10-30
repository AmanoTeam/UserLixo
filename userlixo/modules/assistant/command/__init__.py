from userlixo.decorators import Controller

from .callback_query import CommandCallbackQueryController


@Controller(imports=[CommandCallbackQueryController])
class CommandController:
    pass
