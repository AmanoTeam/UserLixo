from userlixo.decorators import Controller

from .inline_query import IndexInlineQueryController


@Controller(imports=[IndexInlineQueryController])
class InlineIndexController:
    pass
