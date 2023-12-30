from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from langs import Langs

from userlixo.database import Config
from userlixo.modules.common.restart import self_restart_process
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
            return await cls._on_error(text) if callable(cls._on_error) else None

        stdout, process = await get_git_status()
        if process.returncode != 0:
            await git_merge_abort()

            text = compose_upgrade_failed_message(lang, current_branch, process.returncode, stdout)
            return await cls._on_error(text) if callable(cls._on_error) else None

        if "Your branch is up to date" in stdout:
            revision = await get_current_commit_short_revision()
            date = await get_current_commit_date()

            timezone = await get_current_commit_timezone()
            timezone = timezone_shortener(timezone)
            date += f" ({timezone})"

            commits_count = await get_current_commits_count()

            text = compose_already_uptodate_message(lang, revision, date, commits_count)
            return await cls._on_exception(text) if callable(cls._on_exception) else None

        stdout, process = await git_pull_from_branch(current_branch)

        if process.returncode != 0:
            await git_merge_abort()

            text = compose_upgrade_failed_message(lang, current_branch, process.returncode, stdout)
            return await cls._on_error(text) if callable(cls._on_error) else None

        text = compose_before_upgrade_message(lang)
        if callable(cls._on_success):
            await cls._on_success(text)

        self_restart_process()
        return None


def compose_before_upgrade_message(lang: Langs):
    return lang.upgrading_now_alert


def compose_not_git_error_message(lang: Langs):
    return lang.upgrade_error_not_git


def compose_upgrade_failed_message(lang: Langs, branch: str, code: int, output: str):
    return lang.upgrade_failed(branch=branch, code=code, output=output)


def compose_already_uptodate_message(lang: Langs, rev: str, date: str, local_version: int):
    return lang.upgrade_alert_already_uptodate(rev=rev, date=date, local_version=local_version)


def get_branch_if_is_git():
    try:
        head_file = Path(".git/HEAD")
    except FileNotFoundError:
        return None

    with head_file.open(encoding="utf-8") as f:
        content = f.read().splitlines()

    for line in content:
        if line.startswith("ref:"):
            return line.partition("refs/heads/")[2].strip()

    return None


async def get_git_status():
    stdout, process = await shell_exec("git fetch && git status -uno")

    return stdout, process


async def git_merge_abort():
    await shell_exec("git merge --abort")


async def get_current_commit_short_revision():
    return (await shell_exec("git rev-parse --short HEAD"))[0]


async def get_current_commit_date():
    return (await shell_exec('git log -1 --format=%cd --date=format:"%d/%m %H:%M"'))[0]


async def get_current_commit_timezone():
    return (await shell_exec('git log -1 --format=%cd --date=format:"%z"'))[0]


async def get_current_commits_count():
    commits_count = (await shell_exec("git rev-list --count HEAD"))[0]

    return int(commits_count)


async def git_pull_from_branch(branch: str):
    stdout, process = await shell_exec(f"git pull --no-edit origin {branch}")

    return stdout, process


async def save_before_upgrade_message_info(message_id: int, chat_id: int, from_client: str):
    query = Config.delete().where(Config.key == "restarting_alert")
    query.execute()

    timestamp = datetime.now().timestamp()

    Config.create(
        key="restarting_alert",
        value=f"{message_id}|{chat_id}|{timestamp}|upgrade{from_client}",
    )
