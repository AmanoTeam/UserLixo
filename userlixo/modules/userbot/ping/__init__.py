from userlixo.decorators import Controller

from .message import PingMessageController


@Controller(imports=[PingMessageController])
class PingController:
    pass
