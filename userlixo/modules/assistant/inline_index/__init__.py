from userlixo.decorators import controller

from .inline_query import IndexInlineQueryController


@controller(imports=[IndexInlineQueryController])
class InlineIndexController:
    pass
