import io
import re
from typing import Callable

from userlixo.utils import shell_exec


async def cmd(code, on_result: Callable, on_huge_result: Callable, on_no_result: Callable):
    output, process = await shell_exec(code)

    if not output:
        return await on_no_result()

    if len(output) <= 4096:
        output = re.sub(f'([{re.escape("```")}])', r'\\\1', output)

        text = "```bash\n" + output + "\n```"

        return await on_result(text)

    strio = io.BytesIO()
    strio.name = "output.txt"
    strio.write(output.encode())
    await on_huge_result(strio)
