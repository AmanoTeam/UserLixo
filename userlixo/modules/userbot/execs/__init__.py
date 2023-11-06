from userlixo.decorators import controller

from .message import ExecsMessageController


@controller(imports=[ExecsMessageController])
class ExecsController:
    pass
