from voltage.ext.commands import (
        CommandsClient,
        Cog,
        CommandContext
)

from voltage import SendableEmbed

from stk.api import *
from log import log
import globals
from config import getConfig
from utils.flagconverter import flagconverter
import asyncpg
import time
import math
import random

def setup(client: CommandsClient) -> Cog:

    _ = Cog('stk-player-track', 'Reimplemention of the player tracking module from snakebot')

    @_.command(name="seen", description = "See when the user was last detected/online", aliases=["stk-seen"])
    async def stk_seen(ctx: CommandContext, player: str = None):
        sql_esc = str.maketrans({
            "%": "\\%",
            "_": "\\_",
            "\\": "\\\\"
        })

        if player:

            data = await globals.prepared_select.fetchrow(player.translate(sql_esc) + "%")

            if data is None:
                log('STKSeen', f'Player {player} not found in DB')

                return await ctx.reply(embed=SendableEmbed(
                    title = 'Unknown player',
                    description = f"I have not seen this player before.\nCheck the spelling or track them by executing `{ctx.prefix}trackuser {player}`",
                    color = globals.accentcolor
                ))
            else:
                log('STKSeen', f'Player {player} found! Result = {data["username"]}')
                if data["username"] in globals.onlinePlayers:
                    return await ctx.reply(embed=SendableEmbed(
                        title = f"Information for user {flagconverter(str(data['country']))} {data['username']}",
                        description = f"""{flagconverter(str(data["country"]))} {data["username"]} is **currently online**.

Currently in server: {flagconverter(globals.onlinePlayers[data["username"]].attrib["country_code"])} **{globals.onlinePlayers[data["username"]].attrib["name"]}**
""",
                        color = globals.accentcolor
                    ))
                else:
                    return await ctx.reply(embed=SendableEmbed(
                        title = f"Information for user {flagconverter(str(data['country']))} {data['username']}",
                        description = f"""{flagconverter(str(data["country"]))} {data["username"]} is **offline**.

Date last seen: <t:{math.floor(data["date"].timestamp()) - time.timezone}:F>, <t:{math.floor(data["date"].timestamp()) - time.timezone}:R>
Last seen on: {flagconverter(str(data["server_country"]))} **{data["server_name"]}**""",
                        color = globals.accentcolor
                    ))
        else:
            return await ctx.reply(embed=SendableEmbed(
                description = "Please specify a player name. (If partial, will result in closely matching one.)",
                color = globals.accentcolor
            ))

    @_.command(name="trackuser", description = "Track a user privately. Will notify you in Direct Messages if the specified player(s) join or leave a server.", aliases=["stk-trackuser-dm"])
    async def stk_trackuser(ctx: CommandContext, player: str = None):
        
        if player is None:
            return await ctx.reply(embed=SendableEmbed(
                description = "Please specify a player.",
                color = globals.accentcolor
            ))

        if ctx.author.id == "01FHGJ3NPP7XANQQH8C2BE44ZY":
            # Force the discord peasants to use Revolt

            return await ctx.reply("oh u want 2 track a player? use [revolt](https://revolt.chat) lmao")

        data = await globals.prepared_ptrack_query.fetchrow(ctx.author.id)

        if data is not None:
            if player in data["usernames"]:

                return await ctx.reply(embed=SendableEmbed(
                    description = f"You are already tracking {player}",
                    color = globals.accentcolor
                ))

        if len(data["usernames"]) >= getConfig("user_ptrack_max"):
        
            title = "Maximum amount of tracked players exceeded"

            if random.randint(0, 16) == 8:
                title = "You like stalking people eh?"

            return await ctx.reply(embed=SendableEmbed(
                title = title,
                description = f"You have reached the maximum amount of players you can track. You can only track up to **{getConfig('user_ptrack_max')}** players.",
                color = globals.accentcolor
            ))

        await globals.pgconn.execute("""
        INSERT INTO lina_ptrack VALUES ($1, $2) 
        ON CONFLICT (id) DO UPDATE SET usernames = array_append(lina_ptrack.usernames, $3)""",
        ctx.author.id, {player}, player)

        await ctx.reply(embed=SendableEmbed(
            title = f"Tracking {player} privately.",
            description = f"Okay, I will direct message you everytime the user joins or leaves a server. To stop me from tracking {player}, execute `{ctx.prefix}untrackuser {player}`.",
            color = globals.accentcolor
        ))

    @_.command(name="untrackuser", description="Stops tracking the user you speifcied", aliases=["stk-untrackuser-dm"])
    async def stk_untrackuser(ctx: CommandContext, player: str = None):

        if player is None:
            return await ctx.reply(embed=SendableEmbed(
                description = "Please specify a player.",
                color = globals.accentcolor
            ))

   
        data = await globals.prepared_ptrack_query.fetchrow(ctx.author.id)

        if player not in data["usernames"]:

            return await ctx.reply(embed=SendableEmbed(
                description = "You are not currently tracking this player.",
                color = globals.accentcolor
            ))

        await globals.pgconn.execute("UPDATE lina_ptrack SET usernames = array_remove(lina_ptrack.usernames, $1) WHERE id = $2", player, ctx.author.id)

        await ctx.reply(embed=SendableEmbed(
            title = f"No longer tracking {player}.",
            description = f"Okay, I will no longer be tracking {player} for you.",
            color = globals.accentcolor
        ))

    @_.command(name="usertracks", description="See the players you're currently tracking.", aliases=["stk-usertracks-dm"])
    async def stk_usertracks(ctx: CommandContext):

        data = await globals.prepared_ptrack_query.fetchrow(ctx.author.id)

        if not data:
            return await ctx.reply(embed=SendableEmbed(
                description = "You are not registered in the database.",
                color = globals.accentcolor
            ))

        if len(data["usernames"]) == 0:
            return await ctx.reply(embed=SendableEmbed(
                title = "You aren't tracking any players yet.",
                description = f"To start tracking players, execute `{ctx.prefix}trackuser <username>`.",
                color = globals.accentcolor
            ))

        await ctx.reply(embed=SendableEmbed(
            title = f"Players you're currently tracking",
            description = ", ".join(data["usernames"]),
            color = globals.accentcolor
        ))

    return _

