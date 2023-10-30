from userlixo.decorators import Controller

from .message import ExecsMessageController


@Controller(imports=[ExecsMessageController])
class ExecsController:
    pass
