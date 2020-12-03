from pyrogram import Client, filters
from pyromod.helpers import ikb
from pyromod.nav import Pagination
from userlixo.config import cmds

@Client.on_callback_query(filters.sudoers & filters.regex('^list_commands (?P<page>\d+)'))
async def on_list_commands_cq(c, cq):
    await on_list_commands_u(c,cq)

async def on_list_commands_u(c,u):
    lang = u._lang
    is_query = hasattr(u, 'data')
    page = int(u.matches[0]['page'])
    
    item_format = 'info_command {} {}'
    page_format = 'list_commands {}'
    
    layout = Pagination(
        [*cmds.items()],
        item_data=lambda i, pg: item_format.format(i[0], pg),
        item_title=lambda i, pg: i[0],
        page_data=lambda pg: page_format.format(pg)
    )
    
    lines = layout.create(page, columns=2, lines=3)
    if is_query:
        lines.append([(lang.back, 'start')])
    
    keyb = ikb(lines)
    await (u.edit if is_query else u.reply)(lang.commands_text, keyb)

@Client.on_callback_query(filters.sudoers & filters.regex('^info_command (?P<cmd>.+) (?P<pg>\d+)'))
async def on_info_command(c,cq):
    lang = cq._lang
    cmd = cq.matches[0]['cmd']
    pg = int(cq.matches[0]['pg'])
    if cmd not in cmds:
        return await cq.answer(lang.unknown_command)
    
    info = lang.strings[lang.code].get(f'cmd_info_{cmd}', cmds[cmd])
    
    if len(info) < 100:
        return await cq.answer('ℹ️ '+info, show_alert=True)
    
    kb = ikb([
        [(lang.back, f'list_commands {pg}')]
    ])
    text = lang.command_info
    text.escape_html = False
    await cq.edit(text(command=cmd, info=info), kb)