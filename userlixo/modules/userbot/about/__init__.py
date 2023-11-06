from userlixo.decorators import controller

from .message import AboutMessageController


@controller(imports=[AboutMessageController])
class AboutController:
    pass
