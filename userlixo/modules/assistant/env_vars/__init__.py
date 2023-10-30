from userlixo.decorators import Controller

from .callback_query import EnvVarsCallbackQueryController


@Controller(imports=[EnvVarsCallbackQueryController])
class EnvVarsController:
    pass
