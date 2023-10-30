from userlixo.decorators import Controller

from .message import WebAppMessageController


@Controller(imports=[WebAppMessageController])
class WebAppController:
    pass
