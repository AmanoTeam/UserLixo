from userlixo.decorators import controller

from .message import UpgradeMessageController


@controller(imports=[UpgradeMessageController])
class UpgradeController:
    pass
