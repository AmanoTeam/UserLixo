import asyncio
import base64
import click
import configparser
import dotenv.parser
import json
import os
import pyrogram.errors
import sys

from dotenv import get_key, set_key
from rich import print

def raise_ex(e):
    raise e

def b64encode(value:str):
    return base64.b64encode(value.encode()).decode()
def b64decode(value:str):
    return base64.b64decode(value.encode()).decode()


async def main():
    config = configparser.ConfigParser()
    text = '[bold dodger_blue1]Almost there![/]\n[deep_sky_blue1]Now we are going to login into the user and bot accounts.'
    if __name__ == '__main__':
        text = '[bold dodger_blue1 underline]Welcome to UserLixo![/]\n[deep_sky_blue1]We are going to login into the user account to get PYROGRAM_CONFIG and PYROGRAM_SESSION values.'
    text += "\n\nYou will be asked for a value for each var, but you can just press enter to use the default value (if there be any). Let's get started![/]"
    print(text)
    
    if os.path.exists('config.ini'):
        config.read('config.ini')
    elif os.path.exists(os.path.expanduser('~/.pyrogramrc')):
        config.read(os.path.expanduser('~/.pyrogramrc'))
    
    config.setdefault('pyrogram', {})
    
    fields = ['api_id', 'api_hash']
    
    for key in fields:
        text = f"\n┌ [light_sea_green]{key}[/light_sea_green]"
        if key in config['pyrogram']:
            text += f" [deep_sky_blue4](default: {config['pyrogram'][key]})[/]"
        print(text)
        
        try:
            user_value = input('└> ')
        except (KeyboardInterrupt, EOFError):
            print('[red1]Operation cancelled by user')
            exit()
        if not user_value:
            user_value = config['pyrogram'].get(key, '')
        if not user_value:
            print(f'[red1]{key} is required, cannot be empty.')
            exit()
        config['pyrogram'][key] = user_value
    
    with open('config.ini','w') as fp:
        config.write(fp)
    
    from pyrogram import Client
    login_user = True
    if os.path.exists('user.session'):
        async with Client('user', workdir='.', config_file='./config.ini', plugins={'enabled':False}) as user:
            me = await user.get_me()
        mention = '@'+me.username if me.username else me.first_name
        print(f'[bold yellow]I found an existing session from account [/][cyan]{mention}[/][bold yellow]. Do you want to use it?[/] [cyan]\[yn][/]', end='')
        c = click.getchar(True)
        login_user = (c == 'n')
    
    if login_user:
        print('\n\n[bold green]- Logging in and creating new user.session...')
        
        if os.path.exists('user.session'):
            os.remove('user.session')
    else:
        print('\n\n[bold green]- Logging in using existing user.session...')
    user = Client('user', workdir='.', config_file='./config.ini', plugins={'enabled':False})
    await user.start()
    
    session_config = {k:v for section in config.sections() for k,v in config.items(section)}
    session_config = json.dumps(session_config)
    session_config = b64encode(session_config)
    
    session_string = await user.export_session_string()
    
    me = await user.get_me()
    mention = f"@{me.username}" if me.username else me.first_name
    print(f"[green]- OK! Logged in as {mention}[/]")
    
    if __name__ == '__main__':
        print("\nYour PYROGRAM_CONFIG (SENSITIVE DATA, DO NOT SHARE):")
        print(f'[blue]{session_config}[/]')
        
        print("\nYour PYROGRAM_SESSION (SENSITIVE DATA, DO NOT SHARE):")
        print(f'[blue]{session_string}[/]\n')
        return await user.stop()
    
    login_bot = True
    if os.path.exists('bot.session'):
        async with Client('bot', workdir='.', config_file='./config.ini', plugins={'enabled':False}) as bot:
            me = await bot.get_me()
        mention = '@'+me.username
        print(f'[bold yellow]I found an existing session from bot [/][cyan]{mention}[/][bold yellow]. Do you want to use it? [/][cyan]\[yn]', end='')
        c = click.getchar(True)
        login_bot = (c == 'n')
    
    print('\n[bold green]- Logging in the assistant bot...')
    if login_user:
        if os.path.exists('bot.session'):
            os.remove('bot.session')
    if 'BOT_TOKEN' not in os.environ:
        text = f"\n┌ [light_sea_green]BOT_TOKEN[/light_sea_green]"
        print(text)
        
        try:
            user_value = input('└> ')
        except (KeyboardInterrupt, EOFError):
            print('[red1]Operation cancelled by user')
            exit()
        if not user_value:
            print(f'[red1]BOT_TOKEN is required, cannot be empty.')
            exit()
        os.environ['BOT_TOKEN'] = user_value
    
    try:
        bot = Client('bot', workdir='.', config_file='./config.ini', plugins={'enabled': False}, bot_token=os.getenv('BOT_TOKEN'))
        await bot.start()
    except pyrogram.errors.AccesTokenInvalid as e:
        print('[red1]The bot access token is invalid')
        exit()
        
    me = await bot.get_me()
    print(f"[green]- OK! Registered @{me.username} as assistant bot.[/]")
    
    await user.stop()
    await bot.stop()

if __name__ == '__main__':
    asyncio.run(main())