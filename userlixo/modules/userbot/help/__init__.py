from userlixo.decorators import controller

from .message import HelpMessageController


@controller(imports=[HelpMessageController])
class HelpController:
    pass
