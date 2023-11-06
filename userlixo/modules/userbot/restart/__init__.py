from userlixo.decorators import controller

from .message import RestartMessageController


@controller(imports=[RestartMessageController])
class RestartController:
    pass
