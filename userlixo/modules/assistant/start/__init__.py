from userlixo.decorators import Controller

from .callback_query import StartCallbackQueryController
from .message import StartMessageController


@Controller(imports=[StartMessageController, StartCallbackQueryController])
class StartController:
    pass
