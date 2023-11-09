import re
from dataclasses import dataclass

from userlixo.types.plugin_settings import PluginSettings
from userlixo.types.settings_type import SettingsType


@dataclass
class ValidatePluginSettings:
    settings: dict[str, PluginSettings]

    def check(self, values: dict[str, str | int | bool]) -> dict[str, list[str]]:
        errors = {}

        for k, v in values.items():
            if k not in self.settings:
                errors[k] = ["This setting does not exist."]
                continue

            setting = self.settings[k]
            errors[k] = ValidateSettingValue(setting).check(v)

        return errors


@dataclass
class ValidateSetting:
    setting: PluginSettings

    def check(self) -> list[str]:
        errors = []

        if not isinstance(self.setting.type, SettingsType):
            errors.append(f"invalid type: {self.setting.type}")

        if not isinstance(self.setting.label, str):
            errors.append("label must be a string")

        if self.setting.label.strip() == "":
            errors.append("label cannot be empty")

        if self.setting.description and not isinstance(self.setting.description, str):
            errors.append("description must be a string")

        if self.setting.type == SettingsType.select and not len(self.setting.options):
            errors.append("select type requires options")

        if self.setting.type == SettingsType.text:
            errors.extend(self.str())
        elif self.setting.type == SettingsType.int:
            errors.extend(self.int())
        elif self.setting.type == SettingsType.bool:
            errors.extend(self.bool())
        elif self.setting.type == SettingsType.select:
            errors.extend(self.select())

        return errors

    def str(self) -> list[str]:
        setting = self.setting
        errors = []

        if setting.pattern and not isinstance(setting.pattern, str):
            errors.append("pattern must be a string")

        if setting.min_length is not None:
            if not isinstance(setting.min_length, int):
                errors.append("min_length must be an integer")
            if setting.min_length < 0:
                errors.append("min_length must be greater than zero")

            if setting.max_length and setting.min_length > setting.max_length:
                errors.append("min_length must be less than max_length")

        if setting.max_length is not None:
            if not isinstance(setting.max_length, int):
                errors.append("max_length must be an integer")

            if setting.max_length < 0:
                errors.append("max_length must be greater than zero")

        if setting.default is not None:
            errors.extend(ValidateSettingValue(setting).str(setting.default))

        return []

    def int(self) -> list[str]:
        errors = []

        if self.setting.min_value and not isinstance(self.setting.min_value, int):
            errors.append("min_value must be an integer")

        if self.setting.max_value and not isinstance(self.setting.max_value, int):
            errors.append("max_value must be an integer")

        if (
            self.setting.min_value
            and self.setting.max_value
            and self.setting.min_value > self.setting.max_value
        ):
            errors.append("min_value must be less than max_value")

        if self.setting.default is not None:
            errors.extend(ValidateSettingValue(self.setting).int(self.setting.default))

        return errors

    def bool(self) -> list[str]:
        errors = []

        if self.setting.default is not None:
            errors.extend(ValidateSettingValue(self.setting).bool(self.setting.default))

        return errors

    def select(self) -> list[str]:
        errors = []

        if self.setting.options and not isinstance(self.setting.options, list):
            errors.append("options must be a list")

        if self.setting.default is not None:
            errors.extend(ValidateSettingValue(self.setting).select(self.setting.default))

        return errors


@dataclass
class ValidateSettingValue:
    setting: PluginSettings

    def check(self, value) -> list[str]:
        if self.setting.type == SettingsType.text:
            return self.str(value)
        if self.setting.type == SettingsType.int:
            return self.int(value)
        if self.setting.type == SettingsType.bool:
            return self.bool(value)
        if self.setting.type == SettingsType.select:
            return self.select(value)

        raise ValueError(f"Invalid setting type: {self.setting.type}")

    def str(self, value: str) -> list[str]:
        errors = []

        if not isinstance(value, str):
            errors.append("This setting must be a string.")

        if self.setting.min_length and len(value) < self.setting.min_length:
            errors.append(f"This setting must have at least {self.setting.min_length} characters.")

        if self.setting.max_length and len(value) > self.setting.max_length:
            errors.append(f"This setting must have at most {self.setting.max_length} characters.")

        if self.setting.pattern and not re.match(self.setting.pattern, value):
            errors.append(f"This setting must match the pattern {self.setting.pattern}.")

        return errors

    def int(self, value) -> list[str]:
        errors = []

        if not isinstance(value, int) and not isinstance(value, str):
            errors.append("This value must be a integer or a string that represents an integer.")
            return errors

        if not isinstance(value, int):
            if not re.match(r"^\d+$", value):
                errors.append("This setting must be an integer.")
                return errors
            value = int(value)

        if self.setting.min_value and value < self.setting.min_value:
            errors.append(f"This setting must be at least {self.setting.min_value}.")

        if self.setting.max_value and value > self.setting.max_value:
            errors.append(f"This setting must be at most {self.setting.max_value}.")

        return []

    def bool(self, value) -> list[str]:
        errors = []

        if not isinstance(value, bool) and not isinstance(value, str):
            errors.append("This value must be a boolean or a string that represents a boolean.")

        if not isinstance(value, bool) and value.lower() not in ("true", "false"):
            errors.append("This setting must be a boolean.")

        return errors

    def select(self, value) -> list[str]:
        errors = []

        if value not in self.setting.options:
            errors.append(
                f"This setting must be one of the following: {', '.join(self.setting.options)}."
            )

        return errors
