# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

import os

from tortoise import Tortoise, connections, fields
from tortoise.backends.base.client import Capabilities
from tortoise.models import Model


class Message(Model):
    key = fields.IntField(pk=True)
    text = fields.CharField(max_length=4096)
    keyboard = fields.JSONField(default=[])


class Config(Model):
    id = fields.IntField(pk=True)
    key = fields.CharField(max_length=255)
    value = fields.CharField(max_length=255)


async def connect_database():
    await Tortoise.init(
        {
            "connections": {
                "bot_db": os.getenv("DATABASE_URL", "sqlite://userlixo/database/database.sqlite")
            },
            "apps": {"bot": {"models": [__name__], "default_connection": "bot_db"}},
        }
    )

    conn = connections.get("bot_db")
    conn.capabilities = Capabilities(
        "sqlite",
        daemon=False,
        requires_limit=True,
        inline_comment=True,
        support_for_update=False,
        support_update_limit_order_by=False,
    )

    # Generate the schema
    await Tortoise.generate_schemas()
