from userlixo.decorators import Controller
from .index_controller import IndexController


@Controller(imports=[
    IndexController,
])
class InlineQueryController:
    pass
