from userlixo.decorators import controller

from .message import StartMessageController


@controller(imports=[StartMessageController])
class StartController:
    pass
