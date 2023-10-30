from userlixo.decorators import Controller

from .callback_query import AboutCallbackQueryController


@Controller(imports=[AboutCallbackQueryController])
class AboutController:
    pass
