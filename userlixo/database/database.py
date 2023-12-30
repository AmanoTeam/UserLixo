# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team


from peewee import *

database = SqliteDatabase('userlixo/database/database.sqlite')


class BaseModel(Model):
    class Meta:
        database = database


class Config(BaseModel):
    key = CharField()
    value = CharField()

    class Meta:
        table_name = 'config'


class Message(BaseModel):
    key = AutoField()
    keyboard = CharField()
    text = CharField()

    class Meta:
        table_name = 'message'


class PluginSetting(BaseModel):
    key = CharField()
    plugin = CharField()
    value = CharField()

    class Meta:
        table_name = 'pluginsetting'


database.connect()
database.create_tables([Config, Message, PluginSetting])