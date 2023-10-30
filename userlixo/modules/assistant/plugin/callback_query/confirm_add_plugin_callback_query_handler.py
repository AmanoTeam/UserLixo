import asyncio
import importlib
import inspect
import json
import math
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from kink import inject
from pyrogram.helpers import ikb
from pyrogram.types import CallbackQuery

from userlixo.config import bot, plugins, user
from userlixo.database import Config
from userlixo.modules.abstract import CallbackQueryHandler
from userlixo.utils.plugins import (
    get_inactive_plugins,
    read_plugin_info,
    reload_plugins_requirements,
)
from userlixo.utils.services.language_selector import LanguageSelector


@inject
@dataclass
class ConfirmAddPluginCallbackQueryHandler(CallbackQueryHandler):
    language_selector: LanguageSelector

    async def handle_callback_query(self, _client, query: CallbackQuery):
        lang = self.language_selector.get_lang()

        module = None

        plugin_type = query.matches[0]["plugin_type"]
        client = (user, bot)[plugin_type == "bot"]

        cache_filename = query.matches[0]["filename"]
        basename = Path(cache_filename).name
        new_filename = "userlixo/modules/" + plugin_type + "/plugins/" + basename

        plugin = read_plugin_info(cache_filename)
        new_notation = re.sub(
            "info_plugin_callback_handler.py$", "", os.path.relpath(new_filename)
        ).replace("/", ".")

        requirements = plugin.get("requirements")
        if requirements:
            dgray = 'echo -e "\033[1;30m"'
            reset = 'echo -e "\033[0m"'
            req_list = requirements.split()
            req_text = "".join(f" ├ <code>{r}</code>\n" for r in req_list[:-1])
            req_text += f" └ <code>{req_list[-1]}</code>"
            text = lang.installing_plugin_requirements
            text.escape_html = False
            await query.edit(text(requirements=req_text))
            os.system(f"{dgray}; {sys.executable} -m pip install {requirements}; {reset}")

        # Safely unload the plugin if existent
        if Path(new_filename).exists():
            try:
                module = importlib.import_module(new_notation)
            except Exception as e:
                return await query.edit(lang.plugin_could_not_load_existent(name=basename, e=e))

            functions = [*filter(callable, module.__dict__.values())]
            functions = [*filter(lambda f: hasattr(f, "modules"), functions)]

            for f in functions:
                for handler in f.handlers:
                    client.remove_handler(*handler)

        os.renames(cache_filename, new_filename)
        plugin = read_plugin_info(new_filename)

        try:
            if module:
                importlib.reload(module)
            module = importlib.import_module(plugin["notation"])
        except Exception as e:
            Path(new_filename).unlink()
            await query.edit(lang.plugin_could_not_load(e=e))
            raise e

        functions = [*filter(callable, module.__dict__.values())]
        functions = [*filter(lambda f: hasattr(f, "modules"), functions)]

        # if not len(functions):
        #     os.remove(new_filename)
        #     return await cq.edit(lang.plugin_has_no_handlers)

        for f in functions:
            for handler in f.handlers:
                client.add_handler(*handler)

        if module:
            r = None
            functions = [*filter(callable, module.__dict__.values())]
            for f in functions:
                if hasattr(f, "__name__") and f.__name__ == "post_install_script":
                    await query.edit(lang.running_post_install_script)
                    if inspect.iscoroutinefunction(f):
                        r = await f()
                    else:
                        r = await asyncio.get_event_loop().run_in_executor(None, f)
                    break

            if r is not None:
                unload = False
                if isinstance(r, tuple | list):
                    if len(r) == 2:
                        if r[0] != 1:
                            await query.edit(lang.plugin_could_not_load(e=r[1]))
                            unload = True
                    else:
                        await query.edit(
                            lang.plugin_could_not_load(
                                e="The return of post_install_script"
                                + " should be like this: (0, 'nodejs not found')"
                            )
                        )
                        unload = True

                else:
                    await query.edit(
                        lang.plugin_could_not_load(
                            e="The return of post_install_script should be a list or tuple"
                        )
                    )
                    unload = True

                if unload:
                    functions = [*filter(lambda f: hasattr(f, "modules"), functions)]

                    for f in functions:
                        for handler in f.handlers:
                            client.remove_handler(*handler)
                    Path(new_filename).unlink()
                    return None

        plugins[plugin_type][basename] = plugin
        reload_plugins_requirements(plugins)

        inactive = await get_inactive_plugins(plugins)

        if plugin["notation"] in inactive:
            inactive = [x for x in inactive if x != plugin["notation"]]
            await Config.get(key="INACTIVE_PLUGINS").update(value=json.dumps(inactive))

        # Discover which page is this plugin listed in
        quant_per_page = 4 * 2  # lines times columns
        page = math.ceil(len(plugins) / quant_per_page)

        keyboard = ikb([[(lang.see_plugin_info, f"info_plugin {basename} {plugin_type} {page}")]])
        text = lang.plugin_added(name=basename)

        await query.edit(text, keyboard)
        return None
