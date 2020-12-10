<img src="https://piics.ml/i/005.png" width="150" align="right">

UserLixo
=========
Multipurpose Python userbot for Telegram

Requirements
============
- Python 3.6+
- An Unix-like OS
- The api_id and api_hash [from your own Telegram app](https://my.telegram.org/apps) (don't worry, it's easy to get them)

Setup
=====
- Start a new tmux or screen session (recommended but not required)
- Install `virtualenv` via pip:
```bash
pip install virtualenv
```
- Create a virtualenv named 'venv' and activate it:
```bash
virtualenv venv && . venv/bin/activate
```

Running
=======
- Just run `python -m userlixo`
At the first run, all requirements will be automatically installed you'll be asked for some configuration and login.
If you are a developer making some modifications, you may want to use the option '--no-updates' to skip the "pip install" part at every startup.

Note: you'll be asked for a BOT_TOKEN. That's the bot that will be the UserLixo assistant and its inline mode must be activated. You do it by sending /setinline to @BotFather.

Heroku
======
Deploying UserLixo in Heroku is easier but requires an extra step. You firstly need to login locally (can be done in your mobile, using Termux) to generate the values PYROGRAM_SESSION and PYROGRAM_CONFIG, that are required to run on Heroku.

First install the requirements: `pip3 install -Ur requirements.txt`
Then login with: `python3 -m userlixo.login`

Once the values are generated, access the button below to deploy a new app and paste the values of PYROGRAM_SESSION and PYROGRAM_CONFIG on the desired places.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/AmanoTeam/UserLixo/tree/userlixo-czp)

Notes
====
If you find any bugs/issues you can report them by:
- Creating a new issue in this repo
- Sending the issue details to [the chat on Telegram](https://t.me/AmanoChat)
- Forking this repo and opening a pull request with the fix

©2020 - [AmanoTeam™](https://amanoteam.com)
