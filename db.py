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
    id = fields.CharField(max_length=255, pk=True)
    value = fields.CharField(max_length=255, default="")
    valuej = fields.JSONField(default={})

class Personal(Model):
    first_name = fields.CharField(max_length=255)
    last_name = fields.CharField(max_length=255)
    description = fields.CharField(max_length=255)
    faked = fields.BooleanField(default=False)
    user_photo = fields.BooleanField(default=False)

class Notes(Model):
    name = fields.CharField(max_length=255, pk=True)
    type = fields.CharField(max_length=255, default="text")
    content = fields.CharField(max_length=4096, default="")
    file = fields.CharField(max_length=255, default="")

class sticker(Model):
    type = fields.CharField(max_length=255, pk=True)
    num = fields.IntField(default=1)

class Fake(Model):
    id = fields.IntField(pk=True, default=0)
    first_name = fields.CharField(max_length=255, default="")
    last_name = fields.CharField(max_length=255, default="")
    description = fields.CharField(max_length=255, default="")
    faked = fields.BooleanField(default=False)
    user_photo = fields.BooleanField(default=False)
    emoji_status = fields.IntField(default=0)

async def connect_database():
    await Tortoise.init(
        {
            "connections": {
                "bot_db": os.getenv("DATABASE_URL", "sqlite://database.sqlite")
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
