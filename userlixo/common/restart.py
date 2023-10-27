import os
import sys
from datetime import datetime
from typing import Literal

from langs import Langs

from userlixo.database import Config


def compose_before_restart_message(lang: Langs):
    text = lang.restarting_now_alert

    return text


async def save_before_restart_message_info(message_id: int, chat_id: int, from_client: Literal["bot", "user"]):
    await Config.filter(key="restarting_alert").delete()

    timestamp = datetime.now().timestamp()
    
    await Config.create(
        **{
            "key": "restarting_alert",
            "value": f"{message_id}|{chat_id}|{timestamp}|restart{from_client}",
        }
    )


def self_restart_process():
    args = [sys.executable, "-m", "userlixo"]
    if "--no-update" in sys.argv:
        args.append("--no-update")
    if "--no-clear" in sys.argv:
        args.append("--no-clear")

    os.execv(sys.executable, args)
