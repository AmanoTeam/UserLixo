from pyrogram import Client, filters
from userlixo.handlers.bot.list_commands import on_list_commands_u

@Client.on_message(filters.su_cmd('(commands|cmds)'))
async def on_list_commands_txt(c, m):
    m.matches = [{"page": 0}]
    await on_list_commands_u(c,m)