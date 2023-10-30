from userlixo.decorators import Controller

from .about_controller import AboutController
from .execs_controller import ExecsController
from .help_controller import HelpController
from .info_controller import InfoController
from .list_commands_controller import ListCommandsController
from .ping_controller import PingController
from .plugin_controller import PluginController
from .restart_controller import RestartController
from .settings_controller import SettingsController
from .start_controller import StartController
from .upgrade_controller import UpgradeController


@Controller(
    imports=[
        AboutController,
        PingController,
        InfoController,
        PluginController,
        ExecsController,
        HelpController,
        StartController,
        SettingsController,
        ListCommandsController,
        RestartController,
        UpgradeController,
    ]
)
class MessageController:
    pass
