from userlixo.decorators import Controller
from .about_controller import AboutController
from .cmd_controller import CmdController
from .info_controller import InfoController
from .ping_controller import PingController
from .plugin_controller import PluginController


@Controller(
    imports=[
        AboutController,
        PingController,
        InfoController,
        PluginController,
        CmdController,
    ]
)
class MessageController:
    pass
