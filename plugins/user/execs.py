import html
import io
import re
import traceback
from contextlib import redirect_stdout

from config import bot

import asyncio
from hydrogram import Client, filters
from hydrogram.enums import ParseMode
from hydrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from locales import use_lang

# Lista global para armazenar tarefas criadas pelo .exec
EXEC_TASKS = []


@Client.on_message(filters.command("exec", prefixes=".") & filters.sudoers)
@use_lang()
async def execs(c: Client, m: Message, t):
    async def run_exec():
        strio = io.StringIO()
        code = re.split(r"[\n ]+", m.text, 1)[1]
        input_text = ""
        if "#input" in code:
            input_text = code.split("#input=", 1)[1].strip()
        exec(
            "async def __ex(c: Client, m: Message, input_text: str): "
            + " ".join("\n " + l for l in code.split("\n"))
        )
        with redirect_stdout(strio):
            try:
                await locals()["__ex"](c, m, input_text)
            except:
                return await m.reply_text(
                    html.escape(traceback.format_exc()), parse_mode=ParseMode.HTML
                )

        # Decodifica o texto para garantir que os caracteres HTML especiais sejam corretamente exibidos
        decoded_output = html.unescape(strio.getvalue())

        if decoded_output:
            out = html.escape(decoded_output)
        else:
            out = t("exec_seucess")

        if len(out) > 4096:
            with io.BytesIO(str.encode(out)) as out_file:
                out_file.name = "exec.txt"
                await m.reply_document(out_file)
        else:
            await m.edit(f"<code>{out}</code>", parse_mode=ParseMode.HTML)

    # Cria a tarefa e adiciona à lista global
    task = asyncio.create_task(run_exec())
    EXEC_TASKS.append(task)


# Comando .execs para listar tarefas pendentes criadas pelo .exec
@Client.on_message(filters.command("execs", prefixes=".") & filters.sudoers)
@use_lang()
async def execs_list(c: Client, m: Message, t):
    global EXEC_TASKS
    EXEC_TASKS = [task for task in EXEC_TASKS if not task.done()]
    if not EXEC_TASKS:
        await m.reply_text("Nenhuma tarefa pendente criada pelo .exec.")
        return

    msg = "Tarefas pendentes do .exec:"
    keyboard = []
    for idx, task in enumerate(EXEC_TASKS, 1):
        status = 'Pendente' if not task.done() else 'Concluída'
        if not task.done():
            keyboard.append([
                InlineKeyboardButton(
                    f"{idx}. {task.get_coro().__name__} - {status}",
                    callback_data=f"kill_exec_{idx-1}"
                )
            ])
    await m.reply(
        msg,
        reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None
    )
    if m.from_user.is_self:
        await m.delete()


@bot.on_callback_query(filters.regex(r"^kill_exec_\d+$") & filters.sudoers)
async def kill_exec_task(c: Client, cq: CallbackQuery):
    await cq.edit_message_text("Processando...")
    idx = int(cq.data.split("_")[-1])
    global EXEC_TASKS
    EXEC_TASKS = [task for task in EXEC_TASKS if not task.done()]
    if idx < 0 or idx >= len(EXEC_TASKS):
        await cq.answer("Tarefa não encontrada ou já finalizada.", show_alert=True)
        return
    task = EXEC_TASKS[idx]
    if not task.done():
        task.cancel()
        await cq.answer("Tarefa cancelada.", show_alert=True)
    else:
        await cq.answer("Tarefa já finalizada.", show_alert=True)
    await cq.message.edit_text("Task cancelled or already completed.", parse_mode=ParseMode.HTML)
