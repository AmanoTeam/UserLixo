from pyrogram import filters
from pyrogram.helpers import ikb

from userlixo.decorators import on_callback_query, Controller


@Controller()
class HelpController:
    @on_callback_query(filters.regex("^help"))
    async def help(self, c, callback_query):
        await callback_query.answer("Help", show_alert=True)

        await callback_query.edit_message_text(
            "Help",
            reply_markup=ikb(
                [
                    [
                        ("🔙 Back", "start"),
                        ("📚 About", "about_userlixo"),
                    ],
                    [
                        ("📝 Commands", "about_commands"),
                        ("🔌 Plugins", "about_plugins"),
                    ],
                ]
            ),
        )
