from userlixo.decorators import Controller
from .about_controller import AboutController


@Controller(imports=[AboutController])
class MessageController:
    pass
