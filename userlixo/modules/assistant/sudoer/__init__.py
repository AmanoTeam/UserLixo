from userlixo.decorators import controller

from .callback_query import SudoerCallbackQueryController
from .message import AddSudoerMessageController


@controller(imports=[AddSudoerMessageController, SudoerCallbackQueryController])
class SudoerController:
    pass
