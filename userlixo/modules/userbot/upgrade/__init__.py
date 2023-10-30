from userlixo.decorators import Controller

from .message import UpgradeMessageController


@Controller(imports=[UpgradeMessageController])
class UpgradeController:
    pass
