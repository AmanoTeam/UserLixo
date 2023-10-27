from langs import Langs
from pyrogram import Client
from pyrogram.helpers import array_chunk, ikb

from userlixo.config import sudoers, user, bot


async def compose_list_sudoers_message(lang: Langs, client: Client, from_user_id: int):
    text = lang.setting_sudoers_text + "\n"

    buttons = []
    added = []
    for user_id in sudoers:
        try:
            user_obj = await client.get_users(user_id)
        except BaseException:
            import traceback

            traceback.print_exc()
            user_obj = None
        user_real_id = user_obj.id if user_obj else user_id
        if user_real_id in added:
            continue
        added.append(user_real_id)

        mention = user_id
        if user_obj:
            mention = (
                f"@{user_obj.username}" if user_obj.username else user_obj.first_name
            )
        text += f"\n👤 {mention}"

        if user_real_id not in ["me", user.me.id, from_user_id]:
            buttons.append((f"🗑 {mention}", f"remove_sudoer {user_id}"))

    lines = array_chunk(buttons, 2)
    if bot.me.username:
        lines.append(
            [
                (
                    lang.add_sudoer,
                    f"https://t.me/{bot.me.username}?start=add_sudoer",
                    "url",
                )
            ]
        )
    lines.append([(lang.back, "settings")])
    keyboard = ikb(lines)

    return text, keyboard
