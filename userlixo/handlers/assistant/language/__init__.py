from userlixo.decorators import Controller

from .callback_query import LanguageCallbackQueryController


@Controller(imports=[LanguageCallbackQueryController])
class LanguageController:
    pass
