from userlixo.decorators import Controller

from .callback_query import SudoerCallbackQueryController
from .message import AddSudoerMessageController


@Controller(imports=[AddSudoerMessageController, SudoerCallbackQueryController])
class SudoerController:
    pass
