from userlixo.decorators import Controller

from .message import SettingsMessageController


@Controller(imports=[SettingsMessageController])
class SettingsController:
    pass
