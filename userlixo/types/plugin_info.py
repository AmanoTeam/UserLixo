from dataclasses import dataclass


@dataclass
class PluginInfo:
    name: str
    description: str
    version: str
    author: str | list[str]
    contributors: list[str]
    requirements: list[str]
    github: str

    zip_path: str
    folder_path: str

    @staticmethod
    def from_dict(data: dict):
        name = data.get("name", "")
        description = data.get("description", "")
        version = data.get("version", "")
        author = data.get("author", "")
        contributors = data.get("contributors", [])
        requirements = data.get("requirements", [])
        github = data.get("github", "")
        zip_path = data.get("zip_path", "")
        folder_path = data.get("folder_path", "")

        return PluginInfo(
            name=name,
            description=description,
            version=version,
            author=author,
            contributors=contributors,
            requirements=requirements,
            github=github,
            zip_path=zip_path,
            folder_path=folder_path,
        )
