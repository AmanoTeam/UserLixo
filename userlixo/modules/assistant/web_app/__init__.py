from userlixo.decorators import controller

from .message import WebAppMessageController


@controller(imports=[WebAppMessageController])
class WebAppController:
    pass
