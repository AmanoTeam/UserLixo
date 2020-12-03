import asyncio
import os

from tortoise import fields
from tortoise import Tortoise
from tortoise.models import Model

class Message(Model):
    key = fields.IntField(pk=True)
    text = fields.CharField(max_length=255)
    keyboard = fields.JSONField(default=[])

class Config(Model):
    id = fields.IntField(pk=True)
    key = fields.CharField(max_length=255)
    value = fields.CharField(max_length=255)

async def connect_database():
    await Tortoise.init({
        'connections': {
            'bot_db': os.getenv('DATABASE_URL', 'sqlite://userlixo/database/database.sqlite')
        },
        'apps': {
            'bot': {'models': [__name__], 'default_connection': 'bot_db'}
        }
    })
    # Generate the schema
    await Tortoise.generate_schemas()