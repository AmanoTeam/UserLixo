from userlixo.decorators import Controller

from .callback_query import PluginCallbackQueryController
from .message import PluginMessageController


@Controller(imports=[PluginCallbackQueryController, PluginMessageController])
class PluginController:
    pass
