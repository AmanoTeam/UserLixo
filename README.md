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
- Install the requirements by running `pip3 install -Ur requirements-sqlite.txt`
- Run `python3 login.py` and login

Running
=======
- Just run `python3 bot.py` (you may want to use tmux or screen to keep it running 24*7)

Heroku
======
Deploying UserLixo in Heroku is easier but requires an extra step. You firstly need to login locally (can be done in your mobile, using Termux) to generate the values PYROGRAM_SESSION and PYROGRAM_CONFIG, that are required to run on Heroku.

First install the requirements: `pip3 install -Ur requirements-sqlite.txt`
Then login normally: `python3 login.py`

Once the values are generated, access the button below to deploy a new app and paste the values of PYROGRAM_SESSION and PYROGRAM_CONFIG on the desired places.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/AmanoTeam/UserLixo/tree/beta)

Notes
====
If you find any bugs/issues you can report them by:
- Creating a new issue in this repo
- Sending the issue details to [the chat on Telegram](https://t.me/AmanoChat)
- Forking this repo and opening a pull request with the fix

©2020 - [AmanoTeam™](https://amanoteam.com)
