from userlixo.types.plugin_settings import PluginSettings


class PluginInfo:
    name: str
    description: str
    version: str
    author: str | list[str]
    contributors: list[str]
    requirements: list[str]
    github: str

    settings: dict[str, PluginSettings] | None

    zip_path: str
    folder_path: str

    def __init__(self):
        self.settings = {}

    def fill_info(self, info_dict: dict):
        self.name = info_dict.get("name", "")
        self.description = info_dict.get("description", "")
        self.version = info_dict.get("version", "")
        self.author = info_dict.get("author", "")
        self.contributors = info_dict.get("contributors", [])
        self.requirements = info_dict.get("requirements", [])
        self.github = info_dict.get("github", "")
        self.zip_path = info_dict.get("zip_path", "")
        self.folder_path = info_dict.get("folder_path", "")

        return self

    def fill_settings(self, settings_dict: dict | None):
        if not settings_dict:
            self.settings = None
            return self

        for k, v in settings_dict.items():
            setting_type = v.get("type", "")
            label = v.get("label", "")
            description = v.get("description", "")
            default = v.get("default", "")
            options = v.get("options", [])
            min_length = v.get("min_length", None)
            max_length = v.get("max_length", None)
            pattern = v.get("pattern", None)
            min_value = v.get("min_value", None)
            max_value = v.get("max_value", None)

            self.settings[k] = PluginSettings(
                type=setting_type,
                label=label,
                description=description,
                default=default,
                options=options,
                min_length=min_length,
                max_length=max_length,
                pattern=pattern,
                min_value=min_value,
                max_value=max_value,
            )

        return self
