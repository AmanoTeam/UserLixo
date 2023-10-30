<img src="https://files.catbox.moe/lgndjy.png" width="150" align="right">

# UserLixo

Multipurpose Python userbot for Telegram

## Requirements

- Python 3.8+
- [Rye](https://rye-up.com/) or [Docker](https://www.docker.com/)
- An Unix-like OS
- The `api_id` and `api_hash` [from your own Telegram app](https://my.telegram.org/apps) (don't worry, it's easy to get
  them)

## Getting started

### With docker

- Run `docker compose up -d && docker attach userlixo`

### Manually

- It's recommended to start a new tmux or screen session_
- Install the project with `rye sync`
- Run the project with `rye run python -m userlixo`

> If you are a developer making some modifications, you may want to use the option `--no-updates` to skip the pip
> updates at every startup and `--no-clear` to skip the clearing of the screen by the script.

## Setup

At the first run, all requirements will be installed and you'll be asked for some configuration to login.

![Screenshot from 2023-07-11 13-16-23](https://github.com/AmanoTeam/UserLixo/assets/29507335/97dc4ef0-1af0-41bb-acc6-1d7e6f01c9ce)


> You'll be asked for a `BOT_TOKEN`. That's the bot that will be UserLixo's assistant and its inline mode **MUST** be
> enabled. You can enable it by sending /setinline to [@BotFather](https://t.me/BotFather).

When you're done, you should be seeing the following message:

![Screenshot from 2023-07-11 13-18-06](https://github.com/AmanoTeam/UserLixo/assets/29507335/e3f4b713-b060-4a8a-9fcb-4f38225a225a)

## Notes

If you find any bugs/issues you can report them by:

- Creating a new issue in this repo
- Sending the issue details to [the chat on Telegram](https://t.me/AmanoChat)
- Forking this repo and opening a pull request with the fix

## License

[MIT](https://github.com/AmanoTeam/UserLixo/blob/userlixo-czp/LICENSE) © 2023 [AmanoTeam™](https://amanoteam.com)
