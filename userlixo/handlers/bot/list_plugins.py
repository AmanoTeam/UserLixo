# For bot command /plugins, userbot .plugins and bot button 'plugins'
from pyrogram import Client, filters
from pyromod.helpers import ikb
from pyromod.nav import Pagination
from userlixo.config import plugins, user, bot
from userlixo.utils import get_inactive_plugins

@Client.on_message(filters.sudoers & filters.regex('^/plugins'))
async def on_list_plugins_m(c,m):
    m.from_bot_handler = True
    await on_list_plugins_u(c,m)

@Client.on_callback_query(filters.sudoers & filters.regex('^list_plugins'))
async def on_list_plugins_cq(c, cq):
    await on_list_plugins_u(c, cq)

async def on_list_plugins_u(c, u):
    # Determining type of update
    is_query = hasattr(u, 'data') 
    lang = u._lang
    
    text = lang.list_plugins_select_type(
        user=('@'+user.me.username if user.me.username else user.me.first_name),
        bot=bot.me.username
    )
    lines = [
        [(lang.user_plugins, 'user_plugins 0'), (lang.bot_plugins, 'bot_plugins 0')]
    ]
    
    kwargs = {"quote": True}
    if is_query:
        lines.append([(lang.back, 'start')])
        del kwargs['quote']
    keyb = ikb(lines)
    await (u.edit if is_query else u.reply)(text, keyb, **kwargs)

@Client.on_callback_query(filters.sudoers & filters.regex('^(?P<type>user|bot)_plugins (?P<page>\d+)'))
async def on_list_plugins_type(c,u):
    # Determining type of update
    is_query = hasattr(u, 'data') 
    
    lang = u._lang
    page = int(u.matches[0]['page'] or 0)
    plugin_type = u.matches[0]['type']
    
    inactive_plugins = await get_inactive_plugins(plugins)
    
    def item_title(i, pg):
        name = i[0]
        notation = i[1]['notation']
        status = '💤' if notation in inactive_plugins else '❇️'
        return f'{status} {name}'
    layout = Pagination(
        [*plugins[plugin_type].items()],
        item_data=lambda i, pg: 'info_plugin {} {} {}'.format(i[0], plugin_type, pg),
        item_title=item_title,
        page_data=lambda pg: '{}_plugins {}'.format(plugin_type, pg)
    )
    
    lines = layout.create(page, lines=4, columns=2)
    
    # if the message is /plugins (sent to bot) or it's a callback query 'plugins'
    if hasattr(u, 'from_bot_handler') or (hasattr(u, 'message') and u.message):
        lines.append([(lang.add_plugin, f'add_plugin {page}')])
    else: # is command to user
        lines.append([(lang.add_plugin, f"t.me/{bot.me.username}?start=plugin_add", 'url')])
    
    if is_query:
        lines.append([(lang.back, 'list_plugins')])
    keyb = ikb(lines)
    await (u.edit if is_query else u.reply)(lang.plugins_text(type=plugin_type), keyb)
