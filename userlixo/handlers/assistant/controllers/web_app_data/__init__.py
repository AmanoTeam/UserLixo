from userlixo.decorators import Controller

from .restart_controller import RestartController
from .save_settings_controller import SaveSettingsController
from .upgrade_controller import UpgradeController


@Controller(
    imports=[
        RestartController,
        SaveSettingsController,
        UpgradeController,
    ]
)
class WebAppDataController:
    pass
