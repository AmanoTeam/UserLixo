from userlixo.decorators import controller

from .callback_query import HelpCallbackQueryController
from .message import HelpMessageController


@controller(imports=[HelpMessageController, HelpCallbackQueryController])
class HelpController:
    pass
