from userlixo.decorators import Controller

from .message import HelpMessageController


@Controller(imports=[HelpMessageController])
class HelpController:
    pass
