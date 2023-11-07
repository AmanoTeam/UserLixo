from dataclasses import dataclass

from userlixo.types.settings_type import SettingsType


@dataclass
class PluginSettings:
    type: SettingsType
    label: str
    description: str | None
    default: str | int | bool | None
    options: list[str | int | bool] | None
