from userlixo.decorators import Controller

from .callback_query import RestartCallbackQueryController
from .message import RestartMessageController
from .web_app_data import RestartWebAppDataController


@Controller(
    imports=[RestartMessageController, RestartCallbackQueryController, RestartWebAppDataController]
)
class RestartController:
    pass
