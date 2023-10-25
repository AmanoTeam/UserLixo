from pyrogram import filters

from userlixo.decorators import on_callback_query, Controller


@Controller()
class HelpController:
    @staticmethod
    @on_callback_query(filters.regex("^help"))
    async def help(c, callback_query):
        await callback_query.answer("Help", show_alert=True)

        await callback_query.edit_message_text(
            "Help",
            reply_markup=c.inline_keyboard(
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
