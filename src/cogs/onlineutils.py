from voltage.ext.commands import (
    CommandsClient,
    Cog,
    CommandContext
)
from voltage import (
    SendableEmbed
)
from stk.api import user
from utils.flagconverter import flagconverter
from utils.bigip import bigip
from config import getConfig
import globals

def setup(client):

    _ = Cog("Online", "")
    
    @_.command(description='Search for a user (max 50 results)', aliases=['su'])
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
                description = "No results :(",
                color = globals.accentcolor
        ))


        await ctx.reply(embed=SendableEmbed(
            title = f"Search results for {query}",
            description = result,
            color = globals.accentcolor
        ))

    @_.command(description = "Get top players.")
    async def topplayers(ctx: CommandContext):

        data = await user.topPlayers()

        result = ""
        place = 1

        for p in data[0]:

            result += f"{place}. {p.get('username')} -- {p.get('scores')} (Max {p.get('max-scores')})\n"
            place += 1

        return await ctx.reply(embed=SendableEmbed(
            title = "Top 10 ranked players",
            description = result,
            color = globals.accentcolor
        ))

    @_.command(description="See online players")
    async def online(ctx: CommandContext):

        data = globals.lastonlinelist
        result = ""

        for i in range(len(data[0])):
            serverInfo = data[0][i][0]
            serverName = serverInfo.attrib["name"].replace('\r', '').replace('\n', '')
            serverCountry = serverInfo.attrib["country_code"]
            currentTrack = serverInfo.attrib["current_track"]
            currentPlayers = int(serverInfo.attrib["current_players"])
            maxPlayers = int(serverInfo.attrib["max_players"])
            password = int(serverInfo.attrib["password"])
            ip = int(serverInfo.attrib["ip"])
            port = int(serverInfo.attrib["port"])

            players = data[0][i][1]

            if len(players) == 0:
                continue

            result += f"\n{':lock: ' if password == 1 else ''}**{serverName} ({bigip(ip)}:{port})**: {len(players)} player{'s' if len(players) > 1 else ''} - {currentTrack if currentTrack != '' else 'None'}:\n"

            for player in players:

                username = player.attrib["username"]
                countrycode = player.attrib["country-code"]

                result += f"{flagconverter(countrycode)} {username}\n"

            if not (currentPlayers - len(players) <= 0):
                result += f"+{currentPlayers - len(players)}\n"

        return await ctx.reply(embed=SendableEmbed(
            title = "Public Online",
            description = result,
            color = globals.accentcolor,
            icon_url = getConfig("embed_icon")
        ))
    return _
        
