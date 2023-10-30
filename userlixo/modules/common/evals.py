import io
import re
import traceback
from collections.abc import Callable

from meval import meval
from pyrogram import Client
from pyrogram.types import Message


async def evals(
    eval_code: str,
    client: Client,
    message: Message,
    on_result: Callable,
    on_error: Callable,
    on_huge_result: Callable,
    on_no_result: Callable,
):
    # Shortcuts that will be available for the user code
    c = client
    m = message
    reply = message.reply_to_message
    user = (reply or message).from_user
    chat = message.chat

    try:
        output = await meval(eval_code, globals(), **locals())
    except BaseException:
        traceback_string = traceback.format_exc()
        text = f"Exception while running the code:\n<pre>{traceback_string}</pre>"
        return await on_error(text)

    output = str(output)

    if not output:
        return await on_no_result()

    if len(output) <= 4096:
        output = re.sub(f'([{re.escape("```")}])', r"\\\1", output)

        text = "```bash\n" + output + "\n```"

        return await on_result(text)

    strio = io.BytesIO()
    strio.name = "output.txt"
    strio.write(output.encode())
    await on_huge_result(strio)
    return None
