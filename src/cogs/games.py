from voltage import SendableEmbed, Messageable
from voltage.ext import commands

from asyncio import TimeoutError
from dotenv import load_dotenv, dotenv_values
from utils.log import *

import random
import json

load_dotenv()

accent = dotenv_values()['accent']

def setup(client: commands.CommandsClient) -> commands.Cog:
    games = commands.Cog(
        name = 'Games',
        description = 'Some STK related games...'
    )

    @games.command('guessaddon', 'Guess the addon based on image')
    async def guessaddon(ctx: commands.CommandContext):

        with open('data/addons.json', 'r') as f:
            data = json.load(f)

        target = random.choice(list(data))

        answer: str = data[target]['name']

        botmsg: Message = await ctx.send(f"![]({data[target]['image']})", embed=SendableEmbed(
            title = 'Guess the addon',
            description = 'Guess what the addon is!',
            color = accentjkmn2
        ))

        try:
            msg = await client.wait_for('message', check=lambda m: m.author.id != client.user.id and m.channel == ctx.channel, timeout=30)
        except TimeoutError:
            await botmsg.edit(embed=SendableEmbed(
                title = "Time's up!",
                description = f'The addon was **{answer}**!',
                color = accent
            ))

            return

        if msg.content.lower() == answer.lower():
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

    return games