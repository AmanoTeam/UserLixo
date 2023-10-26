from userlixo.decorators import Controller
from .about_controller import AboutController
from .command_controller import CommandController
from .env_vars_controller import EnvVarsController
from .help_controller import HelpController
from .language_controller import LanguageController
from .ping_controller import PingController
from .plugin_controller import PluginController
from .restart_controller import RestartController
from .start_controller import StartController
from .sudoer_controller import SudoerController


@Controller(imports=[
    AboutController,
    CommandController,
    EnvVarsController,
    HelpController,
    LanguageController,
    PingController,
    PluginController,
    StartController,
    SudoerController,
    RestartController
])
class CallbackQueryController:
    pass
