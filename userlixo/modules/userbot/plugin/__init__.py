from userlixo.decorators import Controller

from .message import PluginMessageController


@Controller(
    imports=[
        PluginMessageController,
    ]
)
class PluginController:
    pass
