from langs import Langs
from pyrogram.helpers import ikb
from pyrogram.nav import Pagination

from userlixo.config import cmds


def compose_list_commands_message(lang: Langs, page: int, append_back: bool = False):
    item_format = "info_command {} {}"
    page_format = "list_commands {}"

    layout = Pagination(
        [*cmds.items()],
        item_data=lambda i, pg: item_format.format(i[0], pg),
        item_title=lambda i, pg: i[0],
        page_data=page_format.format,
    )

    lines = layout.create(page, columns=2, lines=3)
    if append_back:
        lines.append([(lang.back, "start")])

    text = lang.commands_text
    keyboard = ikb(lines)

    return text, keyboard
