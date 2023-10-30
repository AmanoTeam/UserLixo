from userlixo.decorators import Controller

from .message import AboutMessageController


@Controller(imports=[AboutMessageController])
class AboutController:
    pass
