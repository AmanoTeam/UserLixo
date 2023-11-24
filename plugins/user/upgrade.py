import asyncio
import os
import sys
from pyrogram import Client, filters
from pyrogram.types import Message
from db import Config
from locales import use_lang

# Define a handler function for the upgrade command
@Client.on_message(filters.command("upgrade", prefixes=".") & filters.me)
@use_lang()
async def upgrade(c: Client, m: Message, strings):
    # Try to get the current branch name from the .git/HEAD file
    try:
        with open(os.path.join(".git", "HEAD")) as f:
            branch = f.read().split("/")[-1].rstrip()
    # If the file does not exist, return an error message
    except FileNotFoundError:
        return await m.edit_text(
            strings("not_git_repo")
        )

    # Split the message text by whitespace and get the optional branch argument
    parts = m.text.split(maxsplit=1)
    if len(parts) == 2:
        branch = parts[1]
    # Edit the message to indicate that the upgrade is in progress
    msg = await m.edit(strings("upgrade_in_progress").format(branch=branch))
    # Create a subprocess to execute the git pull command with the given branch
    proc = await asyncio.create_subprocess_shell(
        f"git pull --no-edit origin {branch}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    # Wait for the subprocess to finish and get the standard output
    stdout = (await proc.communicate())[0]
    # If the subprocess exited with zero, check if the upgrade was successful
    if proc.returncode == 0:
        # If the output contains "Already up to date.", edit the message to say that there is nothing to upgrade
        if "Already up to date." in stdout.decode():
            await msg.edit(strings("already_up_to_date").format(branch=branch))
        # Otherwise, edit the message to say that the userbot is restarting
        else:
            await msg.edit(strings("restarting"))
            # Save the chat id, message id, and branch name to the database for later use
            await Config.update_or_create(id="upgrade", defaults={"valuej": {"chat_id": msg.chat.id, "message_id": msg.id}})
            # Restart the current process with the same arguments
            os.execl(sys.executable, sys.executable, *sys.argv)
    # If the subprocess exited with a non-zero code, edit the message to show the error message
    else:
        await msg.edit(
            strings("upgrade_failed").format(branch=branch, returncode=proc.returncode, decode=stdout.decode())
        )
        # Create another subprocess to abort the merge operation
        proc = await asyncio.create_subprocess_shell("git merge --abort")
        # Wait for the subprocess to finish
        await proc.communicate()
