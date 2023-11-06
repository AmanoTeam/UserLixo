from userlixo.decorators import controller

from .callback_query import AboutCallbackQueryController


@controller(imports=[AboutCallbackQueryController])
class AboutController:
    pass
