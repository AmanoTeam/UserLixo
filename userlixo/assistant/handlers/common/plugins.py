from langs import Langs
from pyrogram.helpers import ikb
from pyrogram.nav import Pagination

from userlixo.config import user, bot, plugins
from userlixo.utils.plugins import get_inactive_plugins, write_plugin_info


def compose_list_plugins_message(lang: Langs, append_back: bool = False):
    text = lang.list_plugins_select_type(
        user=("@" + user.me.username if user.me.username else user.me.first_name),
        bot=bot.me.username,
    )
    keyboard = ikb(
        [
            [
                (lang.user_plugins, "user_plugins 0"),
                (lang.bot_plugins, "bot_plugins 0"),
            ],
            [(lang.back, "start")] if append_back else [],
        ]
    )

    return text, keyboard


async def compose_list_plugins_by_type_message(
    lang: Langs,
    plugin_type: str,
    page: int,
    show_add_plugin_button: bool = True,
    append_back: bool = False,
):
    inactive_plugins = await get_inactive_plugins(plugins)

    def item_title(i, _pg):
        name = i[0]
        notation = i[1]["notation"]
        status = "💤" if notation in inactive_plugins else "❇️"
        return f"{status} {name}"

    layout = Pagination(
        [*plugins[plugin_type].items()],
        item_data=lambda i, pg: "info_plugin {} {} {}".format(i[0], plugin_type, pg),
        item_title=item_title,
        page_data=lambda pg: "{}_plugins {}".format(plugin_type, pg),
    )

    lines = layout.create(page, lines=4, columns=2)

    # if the message is /plugins (sent to bot) or it's a callback query 'plugins'
    if show_add_plugin_button:
        lines.append([(lang.add_plugin, f"add_plugin {page}")])
    else:  # is command to user
        lines.append(
            [(lang.add_plugin, f"t.me/{bot.me.username}?start=plugin_add", "url")]
        )

    if append_back:
        lines.append([(lang.back, "list_plugins")])
    keyboard = ikb(lines)
    return lang.plugins_text(type=plugin_type), keyboard


async def compose_info_plugin_message(
    lang: Langs, plugin_type: str, plugin_basename: str, page: int
):
    plugin = plugins[plugin_type][plugin_basename]

    status = lang.active
    first_btn = (
        lang.deactivate,
        f"deactivate_plugin {plugin_basename} {plugin_type} {page}",
    )

    inactive = await get_inactive_plugins(plugins)

    if plugin["notation"] in inactive:
        status = lang.inactive
        first_btn = (
            lang.activate,
            f"activate_plugin {plugin_basename} {plugin_type} {page}",
        )
    status_line = "\n" + status

    lines = [
        [
            first_btn,
            (lang.remove, f"remove_plugin {plugin_basename} {plugin_type} {page}"),
        ]
    ]
    if "settings" in plugin and plugin["settings"]:
        lines.append(
            [(lang.settings, f"plugin_settings {plugin_basename} {plugin_type} {page}")]
        )
    lines.append([(lang.back, f"{plugin_type}_plugins {page}")])
    keyboard = ikb(lines)

    text = write_plugin_info(plugins, lang, plugin, status_line=status_line)

    return text, keyboard
