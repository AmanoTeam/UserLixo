from userlixo.decorators import Controller

from .callback_query import SettingsCallbackQueryController
from .message import SettingsMessageController
from .web_app_data import SaveSettingsWebAppDataController


@Controller(
    imports=[
        SettingsMessageController,
        SettingsCallbackQueryController,
        SaveSettingsWebAppDataController,
    ]
)
class SettingsController:
    pass
