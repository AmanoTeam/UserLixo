from userlixo.decorators import Controller

from .message import RestartMessageController


@Controller(imports=[RestartMessageController])
class RestartController:
    pass
