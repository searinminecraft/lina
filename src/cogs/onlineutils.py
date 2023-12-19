from voltage.ext.commands import (
    CommandsClient,
    Cog,
    CommandContext
)
from voltage import (
    SendableEmbed
)
from stk.api import user
from utils import (
    convertAddonIdToName,
    bigip,
    flagconverter)
from config import getConfig
from log import log
import globals
import random


def setup(client: CommandsClient):

    _ = Cog("Online", "")

    @_.command(
        description='Search for a user (max 50 results)',
        aliases=['su'])
    async def searchuser(ctx: CommandContext, query: str):

        mdEscape = str.maketrans({
            "_": "\\_"
        })

        data = await user.userSearch(query)

        result = ""

        for i in data[0]:
            result += f"{i.get('user_name').translate(mdEscape)} ({i.get('id')}) \n"

        if result == "":
            return await ctx.reply(embed=SendableEmbed(
                description="No results :(",
                color=globals.accentcolor
        ))


        await ctx.reply(embed=SendableEmbed(
            title=f"Search results for {query}",
            description=result,
            color=globals.accentcolor
        ))

    @_.command(description="Get top players.")
    async def topplayers(ctx: CommandContext):

        data = await user.topPlayers()

        result = ""
        place = 1

        for p in data[0]:

            result += f"{place}. {p.get('username')} — {round(float(p.get('scores')), ndigits=2)} (Max: {round(float(p.get('max-scores')), ndigits=2)})\n"
            place += 1

        return await ctx.reply(embed=SendableEmbed(
            title="Top 10 ranked players",
            description=result,
            color=globals.accentcolor
        ))

    @_.command(description="See online players")
    async def online(ctx: CommandContext):

        data = globals.lastonlinelist
        result = ""

        for i in range(len(data[0])):
            serverInfo = data[0][i][0]
            serverName = serverInfo.attrib["name"] \
                .replace('\r', '') \
                .replace('\n', '')
            currentTrack = serverInfo.attrib["current_track"]
            currentPlayers = int(serverInfo.attrib["current_players"])
            password = int(serverInfo.attrib["password"])
            ip = int(serverInfo.attrib["ip"])
            port = int(serverInfo.attrib["port"])

            players = data[0][i][1]

            if len(players) == 0:
                continue

            if bigip(ip) in getConfig("ip_blacklist"):
                log("Online",
                    f"Warning: Skipping {serverName} because it's IP ({bigip(ip)}) is blacklisted.")
                continue

            result += f"\n{'' if password == 1 else '*'}*{serverName} ({bigip(ip)}:{port})*{'' if password == 1 else '*'}: {len(players)} player{'s' if len(players) > 1 else ''} - {convertAddonIdToName(currentTrack) if currentTrack != '' else 'None'}:\n"

            for player in players:

                username = player.attrib["username"]
                countrycode = player.attrib["country-code"]

                result += f"{flagconverter(countrycode)} {username}\n"

            if not (currentPlayers - len(players) <= 0):
                result += f"+{currentPlayers - len(players)}\n"

        if result == "" or getConfig('debug_noonline'):

            if random.randint(0, 5) == 3:
                return await ctx.send(embed=SendableEmbed(
                    title="Public Offline",
                    description="yes, read the title",
                    color=globals.accentcolor,
                    icon_url=getConfig("embed_icon")
                ))

            return await ctx.send(embed=SendableEmbed(
                title = "Public Online",
                description = random.choice([
                    "Nobody is online... nya~",
                    "Huh? I don't see anyone playing on a server. Maybe check again later?",
                    "Nobody is online, but that's not guaranteed because there might be players not showing up the API.",
                    "Awwww! I guess no one's around to play!",
                    "There's nobody online!!!11",
                    "Nobody's playing. Maybe you can join a server and people will suddenly join.",
                    "No one's online. Probably a geography issue for you.",
                    "Error 404 - Players not found.",
                    "Nobody is online. Have this instead: OwO",
                    "Exception occured: KeyError: \"players\"",
                    "(weird silence)",
                    "See? People are touching grass and you should do the same!",
                    "Nobody's online. Go touch some grass instead.",
                    "More like **public offline**"
                ]),
                color=globals.accentcolor,
                icon_url=getConfig("embed_icon")
            ))

        return await ctx.reply(embed=SendableEmbed(
            title="Public Online",
            description=result,
            color=globals.accentcolor,
            icon_url=getConfig("embed_icon")
        ))
    return _
