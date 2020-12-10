from pyrogram import Client, filters
from userlixo.handlers.user.message import cmd, evals, execs
import re

@Client.on_message(filters.sudoers & filters.regex(r"^/(?P<command>cmd|sh)\s+(?P<code>.+)", flags=re.S))
async def on_cmd_bot(c, m):
    await cmd.cmd(c, m)

@Client.on_message(filters.sudoers & filters.regex(r"^/(?P<cmd>ev(al)?)\s+(?P<code>.+)", flags=re.S))
async def on_eval_bot(c, m):
    await evals.evals(c, m)

@Client.on_message(filters.sudoers & filters.regex(r"^/(?P<cmd>ex(ec)?)\s+(?P<code>.+)", flags=re.S))
async def on_exec_bot(c, m):
    await execs.execs(c, m)