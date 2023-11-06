from userlixo.decorators import controller

from .message import SettingsMessageController


@controller(imports=[SettingsMessageController])
class SettingsController:
    pass
