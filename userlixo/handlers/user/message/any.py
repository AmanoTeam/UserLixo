# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

import os

from pyrogram import Client, filters
from pyrogram.types import Message

from userlixo.config import langs


# Getting the language to use
@Client.on_message(group=-2)
async def deflang(c: Client, m: Message):
    m._lang = langs.get_language(os.getenv("LANGUAGE"))


# Define what updates to reject
@Client.on_edited_message()
async def reject(c: Client, m: Message):
    m.stop_propagation()
