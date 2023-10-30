from userlixo.decorators import Controller

from .message import InfoMessageController


@Controller(imports=[InfoMessageController])
class InfoController:
    pass
