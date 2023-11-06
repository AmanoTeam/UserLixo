from ...decorators import controller
from .about import AboutController
from .execs import ExecsController
from .help import HelpController
from .info import InfoController
from .list_commands import ListCommandsController
from .ping import PingController
from .plugin import PluginController
from .restart import RestartController
from .settings import SettingsController
from .start import StartController
from .upgrade import UpgradeController


@controller(
    imports=[
        AboutController,
        ExecsController,
        HelpController,
        InfoController,
        ListCommandsController,
        PingController,
        PluginController,
        RestartController,
        SettingsController,
        StartController,
        UpgradeController,
    ]
)
class UserbotController:
    pass
