from voltage import SendableEmbed
from voltage.ext import commands
from utils.log import *
import aiohttp

import xml.etree.ElementTree as et
import time
import subprocess
import random
import math
import os
import json

from dotenv import load_dotenv, dotenv_values
load_dotenv()

accent = dotenv_values()['accent']

# Thanks DernisNW for giving the code for converting big ip addresses to readable ones.
def bigip(x):
    return '.'.join([str(y) for y in int.to_bytes(int(x), 4, 'big')])


def setup(client) -> commands.Cog:
    stk = commands.Cog(
        name = 'SuperTuxKart',
        description = 'The core of Lina!'
    )

    @stk.command('online', 'See online users.')
    async def stkonline(ctx: commands.CommandContext):

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

                log('STK', f'Got {len(players)} on {servername}')

                if not players == []:

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

        await ctx.send(embed=SendableEmbed(
            title = 'Online right now in STK',
            description = (result if result != '' else 'Uh, it appears that nobody is online... Have this instead: OwO'),
            color = accent
        ))

    @stk.command('serversearch', 'Search for a server')
    async def serversearch(ctx: commands.CommandContext, *, query: str):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://online.supertuxkart.net/api/v2/server/get-all') as resp:
                data = await resp.text()

        root = et.fromstring(data)
        results = []
        output = ''

        for _ in root[0]:

            if _[0].get('name').lower().find(query.lower()) >= 0:
                results.append(_[0].attrib)

        for result in results:
            servername = result.get('name')
            currtrack = result.get('current_track')
            country = result.get('country_code')
            maxplayers = result.get('max_players')
            currplayers = result.get('current_players')
            password: int = int(result.get('password'))
            ip: int = int(result.get('ip'))
            id: int = int(result.get('id'))
            port: int = int(result.get('port'))

            output += f'**{"".join(chr(127397 + ord(k)) for k in country)} {servername} ({bigip(ip)}:{port})**\n'
            output += f'**Server ID**: {id}\n'
            output += f'**Current Track**: {currtrack}\n'
            output += f'**Password Protected**: {"Yes" if password == 1 else "No"}\n'
            output += f'**Players**: {currplayers}/{maxplayers}\n'
            output += '\n'

        if len(output) > 2000:
            return await ctx.send("Too many results.")

        embed = SendableEmbed(
            title = f'Search Results ({results.__len__()})',
            description = output if output != '' else 'No results :(',
            color = accent
        )

        await ctx.send(embed=embed)

    @stk.command('topranked', 'See top ranked players.')
    async def topranked(ctx: commands.CommandContext):
        load_dotenv()
        log('STK', 'Retrieving top ranked players...')
        data = subprocess.run(['curl', '-sX', 'POST', '-d', f'userid={dotenv_values()["stk_userid"]}&token={dotenv_values()["stk_token"]}', 'https://online.supertuxkart.net/api/v2/user/top-players'], stdout=subprocess.PIPE).stdout.decode('utf-8')
        
        root = et.fromstring(data)
        output = ''
        place = 1

        if root.get('success') == 'no':
            raise Exception(root.get('info'))

        for player in root[0].findall('player'):
            output += f'{place}. **{player.get("username")}**: {math.floor(float(player.get("scores")))}\n'
            place += 1

        embed = SendableEmbed(
            title = 'Top 10 ranked players',
            description = output,
            color = accent
        )

        await ctx.send(embed=embed)

    @stk.command('searchuser', 'Search for a user.')
    async def usersearch(ctx: commands.CommandContext, *, query: str):
        load_dotenv()
        data = subprocess.run(['curl', '-sX', 'POST', '-d', f'userid={dotenv_values()["stk_userid"]}&token={dotenv_values()["stk_token"]}&search-string={query.lower()}', 'https://online.supertuxkart.net/api/v2/user/user-search'], stdout=subprocess.PIPE).stdout.decode('utf-8')
        
        root = et.fromstring(data)
        output = ''

        if root.get('success') == 'no':
            raise Exception(root.get('info'))


        for _ in root[0].findall('user'):
            output += f'* {_.get("user_name")} ({_.get("id")})\n'

        if len(output) > 2000:
            return await ctx.send('I couldn\'t fit all of it due to character limit.')

        embed = SendableEmbed(
            title = f'Search results for "{query}"',
            description = output if output != '' else 'No results :(',
            color = '#f5a9b8'
        )

        await ctx.send(embed=embed)

    @stk.command('account', 'Know what STK account is being used!', ['stk-whoami'])
    async def whoami(ctx: commands.CommandContext):
        load_dotenv()

        embed = SendableEmbed(
            title = 'Who am I?',
            description = f'Hi! I\'m {dotenv_values()["stk_username"]}! User ID: {dotenv_values()["stk_userid"]}',
            color = accent
        )

        await ctx.send(embed=embed)

    @stk.command('pokemap')
    async def pokemap(ctx: commands.CommandContext):
        if not(os.path.exists('data/pokemap.json')):
            f = open('data/pokemap.json', 'w')
            f.close()
            
            with open('data/pokemap.json', 'w') as f:
                json.dump({f"{client.user.id}": {"cooldown": 0, "maps": []}}, f, indent=2)

        with open('data/pokemap.json', 'r') as f:
            data = json.load(f)

        if ctx.author.id not in data:
            data[ctx.author.id] = {'cooldown': 0, 'maps': []}
            with open('data/pokemap.json', 'w') as f:
                json.dump(data, f, indent = 2)
            return await ctx.reply('You have been added to the database. Please re-execute the command!')

        if not data[ctx.author.id]['cooldown'] > time.time():
            with open('data/addons.json', 'r') as f:
                addons = json.load(f)

            addonCaught = random.choice(list(addons))

            data[ctx.author.id]['cooldown'] = time.time() + 7200
            data[ctx.author.id]['maps'].append(addonCaught)

            await ctx.send(embed=SendableEmbed(
                title = 'PokeMap',
                description = f"""<@{ctx.author.id}>, you\'ve caught a **{addons[addonCaught]["name"]}**!
                
                `/installaddon {addonCaught}`""",
                color = accent,
                icon_url = addons[addonCaught]["image"]
            ))
        else:
            return await ctx.send(embed=SendableEmbed(
                title = 'PokeMap',
                description = f"<@{ctx.author.id}>, the command is in cooldown. You can execute it again <t:{math.floor(data[ctx.author.id]['cooldown'])}:R>",
                color = accent
            ))

        with open('data/pokemap.json', 'w') as f:
            json.dump(data, f, indent = 2)

    @stk.command('addondetails', 'Get details of a SuperTuxKart addon.')
    async def addondetails(ctx: commands.CommandContext, addonid: str = None):
        with open('data/addons.json', 'r') as f:
            data = json.load(f)

        if addonid not in data:
            return await ctx.send(embed=SendableEmbed(
                title = 'We\'ve searched far and wide...',
                description = f'Unfortunately, we could not find an addon with ID `{addonid}`.',
                color = accent
            ))

        await ctx.send(embed=SendableEmbed(
            title = f'Addon details of {addonid}',
            description = f"""**Name**: {data[addonid]['name']}
            **Description**:

            ```
            {data[addonid]['description']}
            ```

            **Uploader**: {data[addonid]['uploader']}
            **Designer**: {data[addonid]['designer']}
            **Image**: [here]({data[addonid]['image']})
            **Format**: {data[addonid]['format']}
            **Revision**: {data[addonid]['revision']}
            **Status**: 0x{data[addonid]['status']}
            **Size (MB)**: {math.floor(int(data[addonid]['size']) / 1024000)}
            **Rating**: {int(float(data[addonid]['rating']))}""",
            icon_url = data[addonid]['image'],
            color = accent
        ))

       
    return stk
