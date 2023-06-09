from voltage import (
        SendableEmbed,
        Message,
        CommandNotFound,
        PresenceType
)
from voltage.ext import commands

from utils.log import *
import utils.stkhttp as stk
from utils.bigip import bigip                

from dotenv import dotenv_values, load_dotenv, set_key
import aiohttp

import asyncio
import json
import math
import os
import random
import subprocess
import sys
import time
import xml.etree.ElementTree as et

load_dotenv()

try:
    TOKEN = dotenv_values()['token']
    STK_USERNAME = dotenv_values()['stk_username']
    STK_PASSWORD = dotenv_values()['stk_password']
    ACCENT = dotenv_values()['accent']
    PREFIX = dotenv_values()['prefix']
    STKONLINE_CHANNELID = dotenv_values()['onlineusers_channelid']
except KeyError as k:
    print(f'{k} was not provided. Please set up your .env file properly!')
    sys.exit(1)
    
client = commands.CommandsClient(PREFIX)

async def stkAuth():
    log('STK', f'Authenticating SuperTuxKart Account "{STK_USERNAME}"...', color.RED)

    data = stk.request('POST', 'connect', f'username={STK_USERNAME}&password={STK_PASSWORD}&save_session=true')

    success = data.get('success')
    token = data.get('token')
    userid = data.get('userid')
    
    if success == 'no':
        log('STK', f'Failed to authenticate STK Account "{STK_USERNAME}": {data.get("info")}', color.RED)
        sys.exit(1)

    set_key('.env', "stk_token", token)
    set_key('.env', "stk_userid", userid)

    load_dotenv()

    log('STK', f'Successfully logged in as {STK_USERNAME}.', color.GREEN)

async def updateaddondb():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://online.supertuxkart.net/downloads/xml/online_assets.xml') as resp:
            log('STKAddons', 'Downloading latest addon database.')
            if await resp.text() == '':
                log('STKAddons', 'Unexpected empty string!')
                return

            db = et.fromstring(await resp.text('utf-8'))
    

    if not os.path.exists('data/addons.json'):
        f = open('data/addons.json', 'w')
        f.close()
        
        lis = {}

        for i in db.findall('track'):
            
            if int(i.get('status')) & 0x100:
                lis[i.get('id')] = {**dict(i.attrib)}
                log('STKAddons', f'Registered {i.get("id")} to database.', color.BLUE)
            
        with open('data/addons.json', 'w') as f:
            json.dump(lis, f, indent=2)

    database = json.load(open('data/addons.json'))

    for i in db.findall('track'):
        if i.get('id') not in database:            
            if int(i.get('status')) & 0x100:
                database[i.get('id')] = {**dict(i.attrib)}
                log('STKAddons', f'Registered {i.get("id")} to database.', color.BLUE)

    with open('data/addons.json', 'w') as f:
        json.dump(database, f, indent=2)

async def stkPoll():
    while True:
        log('STK', 'Polling user.')

        data = stk.request('POST', 'poll', f'userid={dotenv_values()["stk_userid"]}&token={dotenv_values()["stk_token"]}')

        if data.get('success') == 'no':
            log('STK', f'STK poll request failed: {data.get("info")}. Attempting to reauthenticate.', color.RED)
            await stkAuth()

        await asyncio.sleep(120)

async def stkonlineloop():
    while True:
        try:

            channel = client.get_channel(STKONLINE_CHANNELID)

            messages = await channel.history()

            if len(messages) == 0:
                msg = await channel.send(f'$%stkonline.{STKONLINE_CHANNELID}%$')
                set_key('.env', 'stkonline_messageid', msg.id)
            else:
                load_dotenv()
                msg = await channel.fetch_message(dotenv_values()['stkonline_messageid'])

            result = ''

            async with aiohttp.ClientSession() as session:
        	    async with session.get('https://online.supertuxkart.net/api/v2/server/get-all') as resp:
        		    data = await resp.text()
        		
            root = et.fromstring(data)

            for _ in root[0]:

                servername = _[0].get('name')
                currtrack = _[0].get('current_track')
                country = _[0].get('country_code')
                maxplayers = _[0].get('max_players')
                currplayers = _[0].get('current_players')
                password: int = int(_[0].get('password'))
                ip: int = int(_[0].get('ip'))
                id: int = int(_[0].get('id'))
                port: int = int(_[0].get('port'))
                players = []


                formattedip = bigip(ip)

                for player in _[1]:
                    players.append([player.get('country-code'), player.get('username'), int(float(player.get('time-played')))])

                if len(players) > 0:

                    result += f'**{"".join(chr(127397 + ord(k)) for k in country)} {servername} ({formattedip}:{port})**\n'
                    result += f'**Server ID**: {id}\n'
                    result += f'**Current Track**: {currtrack}\n'
                    result += f'**Password Protected**: {"Yes" if password == 1 else "No"}\n'
                    result += f'**Players: ({currplayers}/{maxplayers})**\n'
                    result += '```\n'

                    for pesant in players:
                        result += (f'{"".join(chr(127397 + ord(k)) for k in pesant[0])} {pesant[1]} (Played for {pesant[2]} minutes)\n')

                    if not (int(currplayers) - players.__len__() <= 0):
                        result += (f'+{int(currplayers) - players.__len__()}\n')
                    
                    result += '```\n'

                    result += '\n'
                
            if len(players) == 0:
                result += 'Nobody is online... *OwO*\n\n'

            result += f'Last updated: <t:{math.floor(time.time())}:D>, <t:{math.floor(time.time())}:T>\n'
            result += '###### disclaimer: i dont host the bot, so this will mostly be outdated once it goes offline.'

            await msg.edit(embed=SendableEmbed(
                title = 'Online right now in STK',
                description = (result),
                color = ACCENT
            ))

        except Exception as e:
            log('OnlineLoop', f'Error occured! {e}')
            pass
        
        await asyncio.sleep(15)

async def statusloop():
    while True:
        status = [
            'kimden is sweet',
            'Benau be like:',
            'Jan',
            'Python powered!',
            'I use arch btw',
            'My sibling amii is the best!',
            'I love searinminecraft',
            'Avatar drawn by searinminecraft',
            'Mention me for prefix!'
            f'{PREFIX}help for commands!',
            'aeasus',
            'RIP Snakebot :(',
            'https://revolt.cat',
            'My waifus are better than yours!!!!',
            'OwO nyaaaa~~',
            'meow',
            '*purrs cutely*',
            'Install Gentoo',
            'Simple, fast, systemd-free!',
            'OwO whats this?'
        ]

        current = random.choice(status)

        try:
            log('StatusLoop', f'Setting status to "{current}"...')
            await client.set_status(current, PresenceType.online)
        except Exception as e:
            log('StatusLoop', f'Error whilst changing status: {e}')

        await asyncio.sleep(random.randint(15, 60))

@client.error('message')
async def on_error(e: Exception, message: Message):
    if isinstance(e, CommandNotFound):
        return

    log('Commands', f'Error occured: {e}')

    await message.reply(embed=SendableEmbed(
        title = "I'm sorry! An error occured!",
        description = f'`{e}`',
        color = ACCENT
    ))

@client.listen('ready')
async def on_ready():
    log(client.user.name, 'Initializing...')

    await client.set_status('Initializing lina...', PresenceType.focus)
    await stkAuth()
    asyncio.create_task(stkPoll())
    asyncio.create_task(updateaddondb())

    for filename in os.listdir("./src/cogs"):
        if filename.endswith(".py"):
            try:
                client.add_extension(f"cogs.{filename[:-3]}")
                log('Cogs', f'Loaded cog {filename}')
            except Exception as e:
                log('Cogs', e)
    
    asyncio.create_task(statusloop())
    asyncio.create_task(stkonlineloop())
    
    log(client.user.name, 'Initialization complete.', color.GREEN)

@client.listen('message')
async def on_message(message: Message):

    if message.content == f'<@{client.user.id}>':
        return await message.channel.send(embed=SendableEmbed(
        	title = 'Hi there!',
        	description = f'My prefix is `{PREFIX}`',
        	icon_url = client.user.display_avatar.url,
        	color = ACCENT
        ))


    await client.handle_commands(message)

client.run(TOKEN)
