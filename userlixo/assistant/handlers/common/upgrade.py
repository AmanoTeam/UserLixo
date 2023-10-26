from datetime import datetime
from typing import Callable

from langs import Langs

from userlixo.assistant.handlers.common.restart import self_restart_process
from userlixo.database import Config
from userlixo.utils.misc import shell_exec, timezone_shortener


class UpgradeLogicBuilder:
    _on_success: Callable = None
    _on_exception: Callable = None
    _on_error: Callable = None
    lang = None

    @classmethod
    def on_success(cls, func: Callable):
        cls._on_success = func
        return cls

    @classmethod
    def on_exception(cls, func: Callable):
        cls._on_exception = func
        return cls

    @classmethod
    def on_error(cls, func):
        cls._on_error = func
        return cls

    @classmethod
    def set_lang(cls, lang: Langs):
        cls.lang = lang
        return cls

    @classmethod
    async def execute(cls):
        lang = cls.lang

        current_branch = get_branch_if_is_git()
        if not current_branch:
            text = compose_not_git_error_message(lang)
            return await cls._on_error(text) if cls._on_error else None

        stdout, process = await get_git_status()
        if process.returncode != 0:
            await git_merge_abort()

            text = compose_upgrade_failed_message(
                lang, current_branch, process.returncode, stdout
            )
            return await cls._on_error(text) if cls._on_error else None

        if "Your branch is up to date" in stdout:
            revision = await get_current_commit_short_revision()
            date = await get_current_commit_date()

            timezone = await get_current_commit_timezone()
            timezone = timezone_shortener(timezone)
            date += f" ({timezone})"

            commits_count = await get_current_commits_count()

            text = compose_already_uptodate_message(lang, revision, date, commits_count)
            return await cls._on_exception(text) if cls._on_exception else None

        stdout, process = await git_pull_from_branch(current_branch)

        if process.returncode != 0:
            await git_merge_abort()

            text = compose_upgrade_failed_message(
                lang, current_branch, process.returncode, stdout
            )
            return await cls._on_error(text) if cls._on_error else None

        text = compose_before_upgrade_message(lang)
        await cls._on_success(text) if cls._on_success else None

        self_restart_process()


def compose_before_upgrade_message(lang: Langs):
    text = lang.upgrading_now_alert

    return text


def compose_not_git_error_message(lang: Langs):
    text = lang.upgrade_error_not_git

    return text


def compose_upgrade_failed_message(lang: Langs, branch: str, code: int, output: str):
    text = lang.upgrade_failed(branch=branch, code=code, output=output)

    return text


def compose_already_uptodate_message(
    lang: Langs, rev: str, date: str, local_version: int
):
    text = lang.upgrade_alert_already_uptodate(
        rev=rev, date=date, local_version=local_version
    )

    return text


def get_branch_if_is_git():
    try:
        with open(".git/HEAD") as f:
            branch = f.read().split("/")[-1].rstrip()
    except FileNotFoundError:
        return None

    return branch


async def get_git_status():
    stdout, process = await shell_exec("git fetch && git status -uno")

    return stdout, process


async def git_merge_abort():
    await shell_exec("git merge --abort")


async def get_current_commit_short_revision():
    rev, p = await shell_exec("git rev-parse --short HEAD")

    return rev


async def get_current_commit_date():
    date, p = await shell_exec('git log -1 --format=%cd --date=format:"%d/%m %H:%M"')

    return date


async def get_current_commit_timezone():
    timezone, p = await shell_exec('git log -1 --format=%cd --date=format:"%z"')

    return timezone


async def get_current_commits_count():
    commits_count, p = await shell_exec("git rev-list --count HEAD")

    return int(commits_count)


async def git_pull_from_branch(branch: str):
    stdout, process = await shell_exec(f"git pull --no-edit origin {branch}")

    return stdout, process


async def save_before_upgrade_message_info(
    message_id: int, chat_id: int, from_client: str
):
    await Config.filter(key="restarting_alert").delete()

    timestamp = datetime.now().timestamp()

    await Config.create(
        **{
            "key": "restarting_alert",
            "value": f"{message_id}|{chat_id}|{timestamp}|upgrade{from_client}",
        }
    )
