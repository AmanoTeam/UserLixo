from userlixo.decorators import Controller

from .add_sudoer_controller import AddSudoerController
from .execs_controller import ExecsController
from .help_controller import HelpController
from .plugin_controller import PluginController
from .restart_controller import RestartController
from .settings_controller import SettingsController
from .start_controller import StartController
from .upgrade_controller import UpgradeController


@Controller(imports=[
    AddSudoerController,
    ExecsController,
    PluginController,
    RestartController,
    SettingsController,
    StartController,
    UpgradeController,
    HelpController,
])
class MessageController:
    pass
