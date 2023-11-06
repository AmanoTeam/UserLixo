from userlixo.decorators import controller

from .message import InfoMessageController


@controller(imports=[InfoMessageController])
class InfoController:
    pass
