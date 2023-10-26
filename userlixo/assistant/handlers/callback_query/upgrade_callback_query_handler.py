from kink import inject
from pyrogram.helpers import ikb
from pyrogram.types import Message

from userlixo.assistant.handlers.abstract import CallbackQueryHandler
from userlixo.assistant.handlers.common.restart import self_restart_process
from userlixo.assistant.handlers.common.upgrade import get_branch_if_is_git, compose_not_git_error_message, \
    get_git_status, compose_upgrade_failed_message, get_current_commit_short_revision, get_current_commit_date, \
    get_current_commit_timezone, get_current_commits_count, git_merge_abort, compose_already_uptodate_message, \
    compose_before_upgrade_message, git_pull_from_branch, save_before_upgrade_message_info
from userlixo.services.language_selector import LanguageSelector
from userlixo.utils import timezone_shortener


@inject
class UpgradeCallbackQueryHandler(CallbackQueryHandler):
    def __init__(self, language_selector: LanguageSelector):
        self.get_lang = language_selector.get_lang

    async def handle_callback_query(self, _c, m: Message):
        lang = self.get_lang()

        back_keyboard = ikb([
            [(lang.back, "start")]
        ])

        current_branch = get_branch_if_is_git()
        if not current_branch:
            text = compose_not_git_error_message(lang)
            return await m.edit(text, reply_markup=back_keyboard)

        stdout, process = await get_git_status()
        if process.returncode != 0:
            await git_merge_abort()

            text = compose_upgrade_failed_message(lang, current_branch, process.returncode, stdout)
            return await m.edit(text, reply_markup=back_keyboard)

        if "Your branch is up to date" in stdout:
            revision = await get_current_commit_short_revision()
            date = await get_current_commit_date()

            timezone = await get_current_commit_timezone()
            timezone = timezone_shortener(timezone)
            date += f" ({timezone})"

            commits_count = await get_current_commits_count()

            text = compose_already_uptodate_message(lang, revision, date, commits_count)
            return await m.edit(text, reply_markup=back_keyboard)

        text = compose_before_upgrade_message(lang)
        await m.edit(text)

        stdout, process = git_pull_from_branch(current_branch)

        if process.returncode != 0:
            await git_merge_abort()

            text = compose_upgrade_failed_message(lang, current_branch, process.returncode, stdout)
            return await m.edit(text, reply_markup=back_keyboard)

        await save_before_upgrade_message_info(m.id, m.chat.id, "bot")

        self_restart_process()
