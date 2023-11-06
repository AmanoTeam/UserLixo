from userlixo.decorators import controller

from .callback_query import LanguageCallbackQueryController


@controller(imports=[LanguageCallbackQueryController])
class LanguageController:
    pass
