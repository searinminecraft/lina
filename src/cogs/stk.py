from voltage import SendableEmbed, Member
from voltage.ext import commands
from utils.log import *
from utils.bigip import bigip
from utils import stkhttp
import aiohttp
import asyncpg

import xml.etree.ElementTree as et
from datetime import datetime, timezone
import time
import subprocess
import random
import math
import os
import json
from dotenv import load_dotenv, dotenv_values
load_dotenv()

accent = dotenv_values()['accent']
postgresql_conn = dotenv_values()['postgresql_conn']

credentials = f'userid={dotenv_values()["stk_userid"]}&token={dotenv_values()["stk_token"]}&'




def setup(client: commands.CommandsClient) -> commands.Cog:
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

        data = stkhttp.request('POST', 'top-players', credentials)

        output = ''
        place = 1

        for player in data:
            output += f'{place}. **{data[player]["username"]}**: {math.floor(float(data[player]["scores"]))}\n'
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

    @stk.command()
    async def maps(ctx: commands.CommandContext, user: Member = None):
        if user is None:
            user = ctx.author
        with open('data/addons.json', 'r') as f:
            addons = json.load(f)

        conn = await asyncpg.connect(postgresql_conn)
        prepared_data = await conn.prepare('select maps from pokemap where id = $1')
        data = await prepared_data.fetchrow(user.id)

        if data is None:
            return await ctx.reply(f'User {user.name} does not have any maps.')

        output = ''

        for i in data['maps']:
            output += f'* {addons[i]["name"]}\n'

        await ctx.reply(embed=SendableEmbed(
            title = f'{user.name}\'s map collection',
            description = output,
            color = accent,
            icon_url = user.display_avatar.url + '?max_side=64'
        ))
    @stk.command('pokemap')
    async def pokemap(ctx: commands.CommandContext):

        with open('data/addons.json', 'r') as f:
            addons = json.load(f)

        addonCaught = random.choice(list(addons))

        # Thanks DernisNW for helping with the expression. Without him pokemap wouldn't use databases, or even features that need databases.

        insert_pokemap = '''
        insert into pokemap (id, maps, cooldown) values ($1, $2::text[], current_timestamp + '2h' ::interval)
        on conflict (id) do update set maps = array_append(pokemap.maps, $3), cooldown = current_timestamp + '2h' ::interval;
        '''

        sql_pokemap = '''
        select * from pokemap where id = $1;
        '''

        conn = await asyncpg.connect(postgresql_conn)
        prepared_data = await conn.prepare(sql_pokemap)

        data = await prepared_data.fetchrow(ctx.author.id)
        try:
            cooldown = data['cooldown']

            print('cooldown:', cooldown.timestamp())
            print('current:', datetime.now().timestamp())

            if cooldown.timestamp() < datetime.now().timestamp(): pass
            else: return await ctx.reply(embed=SendableEmbed(
                title = 'PokeMap',
                    description = f'Command in cooldown. You can catch another pokemap <t:{math.floor(cooldown.timestamp())}:R>',
                color = accent
            ))
        except: pass
    
        try:
            await conn.execute(insert_pokemap, ctx.author.id, {addonCaught}, addonCaught)
        except Exception as e:
            return await ctx.reply(embed=SendableEmbed(
                title = 'Database error',
                description = f'''A database error occured while processing data. Please contact the author.


### Detailed information:
```
{type(e)}: {e}
```''',
                color = accent
            ))

        await ctx.send(embed=SendableEmbed(
                title = 'PokeMap',
                description = f"""{ctx.author.name}, you\'ve caught a **{addons[addonCaught]["name"]}**!
                
                `/installaddon {addonCaught}`""",
                color = accent,
                icon_url = addons[addonCaught]["image"]
        ))


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

    @stk.command('friendslist', 'Get a user\'s friends list.')
    async def friendslist(ctx: commands.CommandContext, userid: int = None):
        if userid is None:
            return await ctx.reply('Please provide a user id!')
        data = stkhttp.request('POST', 'get-friends-list', f'{credentials}visitingid={userid}')

        result = ''

        for i in data:
            result += f'* {data[i]["user_name"]} ({data[i]["id"]})\n'

        if len(result) > 2000:
            return await ctx.reply(f'They have so many friends I can\'t fit all of it due to the character limit. Sorry about that!\nAnyway, the user has **{len(data)}** friends.')

        await ctx.send(embed=SendableEmbed(
            title = f'Friends of user ID {userid}',
            description = result,
            color = accent
        ))

    @stk.command()
    async def atokas(ctx: commands.CommandContext, user: Member = None):
        if user is None:
            user = ctx.author

        try:
            conn = await asyncpg.connect(postgresql_conn)
            prepared_data = await conn.prepare('select atokas from atokas where id = $1')
            data = await prepared_data.fetchrow(user.id)
        except Exception as e:
             return await ctx.reply(embed=SendableEmbed(
                title = 'Database error',
                description = f'''A database error occured while retrieving data. Please contact the author.


### Detailed information:
```
{type(e)}: {e}
```''',
                color = accent
            ))

        if data is None:
            return await ctx.reply(f'User {user.name} does not have any atokas. Guess they werent appreciated...')
        else:
            return await ctx.send(embed=SendableEmbed(
                title = f"{user.name}'s atokas",
                description = f"{user.name} has {data['atokas']} atokas.",
                icon_url = user.display_avatar.url + '?max_side=64',
                color = accent
            ))       

    return stk

