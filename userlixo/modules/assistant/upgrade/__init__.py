from userlixo.decorators import Controller

from .callback_query import UpgradeCallbackQueryController
from .message import UpgradeMessageController
from .web_app_data import UpgradeWebAppDataController


@Controller(
    imports=[UpgradeMessageController, UpgradeCallbackQueryController, UpgradeWebAppDataController]
)
class UpgradeController:
    pass
