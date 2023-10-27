from userlixo.decorators import Controller
from .about_controller import AboutController
from .info_controller import InfoController
from .ping_controller import PingController


@Controller(imports=[AboutController, PingController, InfoController])
class MessageController:
    pass
