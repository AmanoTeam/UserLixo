# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

import asyncio
import base64
import re


def tryint(value):
    try:
        return int(value)
    except BaseException:
        return value


def b64encode(value: str):
    return base64.b64encode(value.encode()).decode()


def b64decode(value: str):
    return base64.b64decode(value.encode()).decode()


async def shell_exec(code, treat=True):
    process = await asyncio.create_subprocess_shell(
        code, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
    )

    stdout = (await process.communicate())[0]
    if treat:
        stdout = stdout.decode().strip()
    return stdout, process


def timezone_shortener(timezone):
    if timezone[-2:] == "00":  # e.g. -0300 to -03
        timezone = timezone[:-2]
    if timezone[1] == "0":  # e.g. -03 to -3
        timezone = timezone[0] + timezone[2:]
    if re.match(r"[\+-]\d+", timezone):  # if timezone is not "UTC" nor ""
        timezone = "GMT" + timezone
    return timezone
