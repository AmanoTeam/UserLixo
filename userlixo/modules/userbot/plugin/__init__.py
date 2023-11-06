from userlixo.decorators import controller

from .message import PluginMessageController


@controller(
    imports=[
        PluginMessageController,
    ]
)
class PluginController:
    pass
