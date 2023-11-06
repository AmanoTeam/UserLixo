from userlixo.decorators import controller

from .callback_query import PluginCallbackQueryController
from .message import PluginMessageController


@controller(imports=[PluginCallbackQueryController, PluginMessageController])
class PluginController:
    pass
