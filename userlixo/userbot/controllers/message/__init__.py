from userlixo.decorators import Controller
from .about_controller import AboutController
from .execs_controller import ExecsController
from .help_controller import HelpController
from .info_controller import InfoController
from .ping_controller import PingController
from .plugin_controller import PluginController


@Controller(
    imports=[
        AboutController,
        PingController,
        InfoController,
        PluginController,
        ExecsController,
        HelpController,
    ]
)
class MessageController:
    pass
