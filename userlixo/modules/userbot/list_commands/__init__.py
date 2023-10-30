from userlixo.decorators import Controller

from .message import ListCommandsMessageController


@Controller(imports=[ListCommandsMessageController])
class ListCommandsController:
    pass
