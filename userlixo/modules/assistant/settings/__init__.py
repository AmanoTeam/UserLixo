from userlixo.decorators import controller

from .callback_query import SettingsCallbackQueryController
from .message import SettingsMessageController
from .web_app_data import SaveSettingsWebAppDataController


@controller(
    imports=[
        SettingsMessageController,
        SettingsCallbackQueryController,
        SaveSettingsWebAppDataController,
    ]
)
class SettingsController:
    pass
