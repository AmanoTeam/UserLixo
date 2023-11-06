from userlixo.decorators import controller

from .callback_query import EnvVarsCallbackQueryController


@controller(imports=[EnvVarsCallbackQueryController])
class EnvVarsController:
    pass
