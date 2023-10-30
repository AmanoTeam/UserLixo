from userlixo.decorators import Controller

from .callback_query import HelpCallbackQueryController
from .message import HelpMessageController


@Controller(imports=[HelpMessageController, HelpCallbackQueryController])
class HelpController:
    pass
