# UserLixo Plugin Development Guide

## Structure of Plugins

UserLixo empowers developers to create custom plugins to extend its functionality. These plugins are an integral part of the UserLixo ecosystem, allowing you to add new features, automate tasks, and enhance your Telegram experience. In this section, we'll explore the structure of UserLixo plugins, guiding developers on how to create their own and integrate them into UserLixo in 2023.

### Plugin Basics

A UserLixo plugin is essentially a zip file containing at least two key components at the root level: `__init__.py` and `plugin.toml`. These files serve as the backbone of your plugin, defining its identity, functionality, and integration with UserLixo.

#### `__init__.py`

The `__init__.py` file is where you define all the elements that will be loaded into UserLixo. These elements can include user and bot controllers, handlers, pre-load, and post-load functions. Here's a breakdown of these components:

- **User Controllers and Bot Controllers**: UserLixo allows you to define user and bot controllers using decorators `@user_controller` and `@bot_controller`. These controllers define how UserLixo interacts with users and bots, respectively.

- **Handlers**: You can define user and bot handlers using `@user_handler` and `@bot_handler` decorators. Handlers are responsible for processing incoming messages and executing specific actions based on predefined triggers.

- **Pre-Load and Post-Load Functions**: These functions are executed before and after the load of the plugin elements into UserLixo. You can use them for any necessary setup or cleanup operations.

It's essential to note that while the core functionality of your plugin, such as controllers and handlers, should be defined in the `__init__.py`, you can structure your plugin code in any way you prefer. You have the flexibility to organize your code across multiple files (and multiple directory levels) and import the necessary components into the `__init__.py`.

#### `plugin.toml`

The `plugin.toml` file serves as a metadata descriptor for your plugin. It contains a structured object, referred to as "plugin," with the following mandatory keys:

- `name`: The name of your plugin.
- `author`: The name or username of the plugin's author.
- `description`: A brief description of your plugin's purpose.

Additionally, you can include the following optional keys in the `plugin.toml` file to provide more information about your plugin:

- `version`: A string representing the plugin's version.
- `contributors`: A list of names or usernames of contributors to the plugin.
- `requirements`: A list of any dependencies or requirements your plugin relies on.
- `github`: A URL linking to the plugin's source code repository on GitHub or another platform.

##### Example `plugin.toml` File
```toml
[plugin]
name = "AwesomePlugin"
author = "YourUsername"
description = "A plugin that performs awesome tasks in UserLixo"
version = "1.0"
contributors = ["Contributor1", "Contributor2"]
github = "https://github.com/yourusername/awesome-plugin"
requirements = [
    "Pillow>=10.1.0",
    "httpx[http2]>=0.25.1"
]

```
### Example Plugin Structure

Here's an example of how your plugin structure might look:

```
your_plugin/
├── __init__.py
└── plugin.toml
```

In the `__init__.py` file, you'd define your user and bot controllers, handlers, and any pre-load or post-load functions. Meanwhile, the `plugin.toml` file would contain the metadata about your plugin.

By adhering to this structure and providing the necessary information in the `plugin.toml` file, you can easily integrate your custom plugin into UserLixo, enhancing its capabilities and tailoring it to your specific needs.


### Developing Plugins

While developing, you can keep your files under a folder at `userlixo/plugins`. It will be loaded at the startup just like other installed plugins. Once finished, you can zip it up and share with others.
### Zip creation

Once you've created your plugin, you can zip it up and upload it to UserLixo. The zip file should contain the `__init__.py` and `plugin.toml` files at the root level. You can also include any other files or directories you need to support your plugin's functionality.

Recommended command to create the zip file:

```bash
zip ./userlixo/cache/PLUGIN_NAME.zip -r userlixo/plugins/PLUGIN_NAME/* -x "*venv/*" -x "*__pycache__/*" -x "*requirements.txt" -j
```

The command above will create a zip file named `PLUGIN_NAME.zip` in the `userlixo/cache` directory. It will include all the files and directories in the `userlixo/plugins/PLUGIN_NAME` directory, excluding the `venv` directory, `__pycache__` directory, and `requirements.txt` file.
The option `-j` ensures the files at `userlixo/plugins/PLUGIN_NAME/` will be added at the root of the zip file, without creating the structure of parent folders (`userlixo/plugins/PLUGIN_NAME/`).
