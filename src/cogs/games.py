from voltage import SendableEmbed, Message
from voltage.ext import commands

from asyncio import TimeoutError
import asyncpg
from dotenv import load_dotenv, dotenv_values
from utils.log import *

import os
import random
import json

load_dotenv()

accent = dotenv_values()['accent']
db_address = dotenv_values()['postgresql_conn']

def setup(client: commands.CommandsClient) -> commands.Cog:
    games = commands.Cog(
        name = 'Games',
        description = 'Some STK related games...'
    )

    @games.command('guessaddon', 'Guess the addon based on image')
    async def guessaddon(ctx: commands.CommandContext):

        with open('data/addons.json', 'r') as f:
            data = json.load(f)

        if not os.path.exists('data/addonguess.json'):
            f = open('data/addonguess.json', 'w')
            f.close()

            with open('data/addonguess.json', 'w') as f:
                json.dump({f"{client.user.id}": {"score": 0}}, f, indent=2)

        with open('data/addonguess.json', 'r') as f:
            playerdata = json.load(f)

        if ctx.author.id not in playerdata:
            playerdata[ctx.author.id] = {"score": 0}
            with open('data/addonguess.json', 'w') as f:
                json.dump(playerdata, f, indent = 2)

        target = random.choice(list(data))

        answer: str = data[target]['name']

        botmsg: Message = await ctx.send(f"![]({data[target]['image']})", embed=SendableEmbed(
            title = 'Guess the addon',
            description = 'Guess what the addon is!',
            color = accent
        ))

        try:
            msg: Message = await client.wait_for('message', check=lambda m: m.author.id == ctx.author.id and m.channel == ctx.channel, timeout=30)
        except TimeoutError:
            await botmsg.edit(embed=SendableEmbed(
                title = "Time's up!",
                description = f'The addon was **{answer}**!',
                color = accent
            ))

            return

        if msg.content.lower() == answer.lower():

            conn = await asyncpg.connect(db_address)
            try:
                await conn.execute(
                    '''
                    insert into guessaddon_score (id, score) values ($1, 1)
                    on conflict (id) do update set score = guessaddon_score.score + 1;
                    ''',
                    ctx.author.id
                )
            except Exception as e:
                log('Database', f'Error occured while saving score: {e}')

            await botmsg.edit(embed=SendableEmbed(
                title = 'Great job!',
                description = f"""The addon was **{answer}**!
                
                `/installaddon {data[target]['id']}`""",
                color = accent
            ))
        else:
            await botmsg.edit(embed=SendableEmbed(
                title = 'Better luck next time!',
                description = f"Wrong answer. The addon was **{answer}**",
                color = accent
            ))

    @games.command()
    async def topguesses(ctx: commands.CommandContext):
        conn = await asyncpg.connect(db_address)
        
        try:
            prepared_data = await conn.prepare('select * from guessaddon_score')
            playerdata = await prepared_data.fetch()
        except Exception as e:
            log('Database', 'Error occured whule retrieving guessaddon_score: {e}')

        output = ''

        for _ in playerdata:
            output += f'* <@{_["id"]}>: {_["score"]}\n'

        await ctx.send(embed=SendableEmbed(
            title = 'Top 10 guessors in the guessaddon command',
            description = output,
            color = accent
        ))        

    return games
