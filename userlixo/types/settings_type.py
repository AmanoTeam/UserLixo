from enum import Enum


class SettingsType(Enum):
    text = "text"
    bool = "bool"
    int = "int"
    select = "select"
    range = "range"
