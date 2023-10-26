from datetime import datetime

from langs import Langs

from userlixo.database import Config
from userlixo.utils.misc import shell_exec


def compose_before_upgrade_message(lang: Langs):
    text = lang.upgrading_now_alert

    return text


def compose_not_git_error_message(lang: Langs):
    text = lang.upgrade_error_not_git

    return text


def compose_upgrade_failed_message(lang: Langs, branch: str, code: int, output: str):
    text = lang.upgrade_failed(branch=branch, code=code, output=output)

    return text


def compose_already_uptodate_message(lang: Langs, rev: str, date: str, local_version: int):
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


def get_git_status():
    stdout, process = shell_exec("git fetch && git status -uno")

    return stdout, process


def git_merge_abort():
    shell_exec("git merge --abort")


async def get_current_commit_short_revision():
    rev, = await shell_exec("git rev-parse --short HEAD")

    return rev


async def get_current_commit_date():
    date, = await shell_exec(
        'git log -1 --format=%cd --date=format:"%d/%m %H:%M"'
    )

    return date


async def get_current_commit_timezone():
    timezone, = await shell_exec('git log -1 --format=%cd --date=format:"%z"')

    return timezone


async def get_current_commits_count():
    commits_count, = await shell_exec("git rev-list --count HEAD")

    return int(commits_count)


async def git_pull_from_branch(branch: str):
    stdout, process = await shell_exec(f"git pull --no-edit origin {branch}")

    return stdout, process


async def save_before_upgrade_message_info(message_id: int, chat_id: int, from_client: str):
    await Config.filter(key="restarting_alert").delete()

    timestamp = datetime.now().timestamp()

    await Config.create(
        **{
            "key": "restarting_alert",
            "value": f"{message_id}|{chat_id}|{timestamp}|upgrade{from_client}",
        }
    )
