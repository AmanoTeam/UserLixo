<img src="https://files.catbox.moe/lgndjy.png" width="150" align="right">

# UserLixo

Multipurpose Python userbot for Telegram

## Requirements

- Python 3.8+
- [Poetry](https://python-poetry.org/)
- An Unix-like OS
- The `api_id` and `api_hash` [from your own Telegram app](https://my.telegram.org/apps) (don't worry, it's easy to get them)

## Getting started

### With docker

- Run `docker compose up -d && docker attach userlixo`

### Manually

- It's recommended to start a new tmux or screen session_
- Install the project with `poetry install`
- Run the project with `poetry run python -m userlixo`

> If you are a developer making some modifications, you may want to use the option `--no-updates` to skip the pip updates at every startup.

## Setup

At the first run, all requirements will be installed and you'll be asked for some configuration to login.

::PHOTO_PLACEHOLDER::

> You'll be asked for a `BOT_TOKEN`. That's the bot that will be UserLixo's assistant and its inline mode **MUST** be enabled. You can enable it by sending /setinline to [@BotFather](https://t.me/BotFather).

When you're done, you should be seeing the following message:

::PHOTO_PLACEHOLDER::
## Notes

If you find any bugs/issues you can report them by:

- Creating a new issue in this repo
- Sending the issue details to [the chat on Telegram](https://t.me/AmanoChat)
- Forking this repo and opening a pull request with the fix

## License

[MIT](https://github.com/AmanoTeam/UserLixo/blob/userlixo-czp/LICENSE) © 2023 [AmanoTeam™](https://amanoteam.com)
