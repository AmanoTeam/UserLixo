from pyrogram import Client, filters
from pyromod.helpers import ikb
from pyromod.nav import Pagination
from config import cmds

@Client.on_callback_query(filters.sudoers & filters.regex('^list_commands (?P<page>\d+)'))
async def oncommands(c,cq):
    lang = cq.lang
    this_page = int(cq.matches[0]['page'])
    
    item_format = 'info_command {} {}'
    page_format = 'list_commands {}'
    if cq.data.endswith('start'):
        item_format = 'info_command {} {} start'
        page_format = 'list_commands {} start'
    
    page = Pagination(
        [*cmds.items()],
        item_data=lambda i, pg: item_format.format(i[0], pg),
        item_title=lambda i, pg: i[0],
        page_data=lambda pg: page_format.format(pg)
    )
    
    lines = page.create(this_page, columns=2)
    if cq.data.endswith('start'):
        lines.append([(lang.back, 'start')])
    else:
        lines.append([(lang.back, 'help')])
    
    await cq.edit(lang.commands_text, ikb(lines))

@Client.on_callback_query(filters.sudoers & filters.regex('^info_command (?P<cmd>.+) (?P<pg>\d+)'))
async def onshowcommand(c,cq):
    lang = cq.lang
    cmd = cq.matches[0]['cmd']
    pg = int(cq.matches[0]['pg'])
    if cmd not in cmds:
        return await cq.answer('UNKNOWN')
    
    info = lang.strings[lang.code].get(f'cmd_info_{cmd}', cmds[cmd])
    
    if len(info) < 100:
        return await cq.answer('ℹ️ '+info, show_alert=True)
    
    back_data = f'list_commands {pg}'
    if cq.data.endswith('start'):
        back_data.append(' start')
    
    kb = ikb([
        [(lang.back, back_data)]
    ])
    text = lang.command_info
    text.escape_html = False
    await cq.edit(text(command=cmd, info=info), kb)