from userlixo.decorators import controller

from .callback_query import StartCallbackQueryController
from .message import StartMessageController


@controller(imports=[StartMessageController, StartCallbackQueryController])
class StartController:
    pass
