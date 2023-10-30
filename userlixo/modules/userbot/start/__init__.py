from userlixo.decorators import Controller

from .message import StartMessageController


@Controller(imports=[StartMessageController])
class StartController:
    pass
