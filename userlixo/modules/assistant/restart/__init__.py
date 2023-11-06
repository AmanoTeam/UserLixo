from userlixo.decorators import controller

from .callback_query import RestartCallbackQueryController
from .message import RestartMessageController
from .web_app_data import RestartWebAppDataController


@controller(
    imports=[RestartMessageController, RestartCallbackQueryController, RestartWebAppDataController]
)
class RestartController:
    pass
