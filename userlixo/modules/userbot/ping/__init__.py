from userlixo.decorators import controller

from .message import PingMessageController


@controller(imports=[PingMessageController])
class PingController:
    pass
