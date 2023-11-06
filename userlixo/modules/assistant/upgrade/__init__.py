from userlixo.decorators import controller

from .callback_query import UpgradeCallbackQueryController
from .message import UpgradeMessageController
from .web_app_data import UpgradeWebAppDataController


@controller(
    imports=[UpgradeMessageController, UpgradeCallbackQueryController, UpgradeWebAppDataController]
)
class UpgradeController:
    pass
