<img src="https://raw.githubusercontent.com/edubr029/piics/master/i/005.png" width="150" align="right">

# UserLixo

Multipurpose Python userbot for Telegram

## Requirements

### To run locally
*   Python 3.10+
*   An Unix-like operating system

### To run with Docker
*   Docker and Docker compose
*   An Docker-compatible operating system

## Ai comands
*   To configure the artificial intelligences, you need to download the cookie editor in the browser (for Bing to work it needs to be Edge) and open the sites: https://bing.com/chat, and https://gemini.google.com/app. Using the cookie editor, export to JSON and save in the files `cookies.json` and `bard_cookies.json` respectively.

## Ytdl command
*   To configure the ytdl, you need to download an Netscape compatible cookie editor in the browser and open the youtube site. Using the cookie editor, export to TXT and save in the file `ytdl-cookies.txt`.

## Setup (local execution)

*   Install the requirements by running `pip3 install -Ur requirements.txt`
*   For the video kebab to work, install ffmpeg.
*   Go to https://my.telegram.org/apps, create a new app and save its api_id and api_hash
*   Edit ``.env`` file and fill in the data
*   If you have userlixo-rfc 1.0, run the ```convert.py``` to convert the database.
*   Run `python3 bot.py` and login user and bot.

## Running (local execution)

*   Just run `python3 bot.py` (you may also want to use tmux or screen to keep it running 24\*7)

## Setup (docker execution)

*   Go to https://my.telegram.org/apps, create a new app and save its api_id and api_hash
*   Edit ``.env`` file and fill in the data (use `.env.example` as a template)
*   If you have userlixo-rfc 1.0, run the ```convert.py``` to convert the database.

### Using the GitHub Container Registry image (recommended)

1. **Create Telegram sessions (only once):**
```bash
docker compose --profile setup run --rm setup
```
This will ask for:
- Bot token (obtained from @BotFather)
- Phone number and verification code for the userbot

2. **Run the bot:**
```bash
docker compose up -d userlixo
```

### Local build (alternative)

If you prefer to build locally, edit `docker-compose.yml` and replace:
```yaml
image: ghcr.io/erysthon/userlixo:latest
```
with:
```yaml
build: .
```

Then run:
```bash
docker compose --profile setup run --rm setup
docker compose up -d userlixo
```

## Running (docker execution)

*   View logs: `docker compose logs -f userlixo`
*   Stop: `docker compose down`
*   Update: `docker compose pull && docker compose up -d userlixo`

## Notes

Don't forget to run `/config` in the bot's DM to set the language. <br/>
Don't forget to edit ``docker-compose.yml`` file to set the timezone.

If you find any bugs/issues you can report them by:

*   Creating a new issue in this repo
*   Sending the issue details to [the chat on Telegram](https://t.me/UserLixoChat)
*   If you know how to fix the issue, fork this repo and open up a pull request

©2026 - [AmanoTeam™](https://amanoteam.com)
