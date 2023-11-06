from ...decorators import controller
from .about import AboutController
from .command import CommandController
from .env_vars import EnvVarsController
from .execs import ExecsController
from .help import HelpController
from .inline_index import InlineIndexController
from .language import LanguageController
from .ping import PingController
from .plugin import PluginController
from .restart import RestartController
from .settings import SettingsController
from .start import StartController
from .sudoer import SudoerController
from .upgrade import UpgradeController
from .web_app import WebAppController


@controller(
    imports=[
        AboutController,
        CommandController,
        EnvVarsController,
        ExecsController,
        HelpController,
        InlineIndexController,
        LanguageController,
        PingController,
        PluginController,
        RestartController,
        SettingsController,
        StartController,
        SudoerController,
        UpgradeController,
        WebAppController,
    ]
)
class AssistantController:
    pass
