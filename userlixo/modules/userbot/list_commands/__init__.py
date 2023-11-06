from userlixo.decorators import controller

from .message import ListCommandsMessageController


@controller(imports=[ListCommandsMessageController])
class ListCommandsController:
    pass
