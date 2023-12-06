# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team


from peewee import *

database = SqliteDatabase('userlixo/database/database.sqlite')


class UnknownField(object):
    def __init__(self, *_, **__): pass


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
    keyboard = UnknownField()  # JSON
    text = CharField()

    class Meta:
        table_name = 'message'


class PluginSetting(BaseModel):
    key = CharField()
    plugin = CharField()
    value = CharField()

    class Meta:
        table_name = 'pluginsetting'
