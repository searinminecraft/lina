import globals
from voltage import Message, TextChannel, SendableEmbed
from voltage.errors import HTTPError
from voltage.ext.commands import CommandsClient
from time import time
import asyncio

from utils import *
from log import log


async def updateChannels():
    client: CommandsClient = globals.client

    while not globals.lastonlinelist:
        await asyncio.sleep(5)

    while True:
        data = globals.lastonlinelist
        content = ""

        for s in range(len(data[0])):
            serverInfo = data[0][s][0]
            players = data[0][s][1]

            serverName = str(serverInfo.attrib["name"]).replace(r'\r\n', '')
            serverCountry = serverInfo.attrib["country_code"]
            currentTrack = serverInfo.attrib["current_track"]
            currentPlayers = int(serverInfo.attrib["current_players"])
            maxPlayers = int(serverInfo.attrib["max_players"])
            passwordProtected = int(serverInfo.attrib["password"]) == 1
            ip = int(serverInfo.attrib["ip"])
            port = int(serverInfo.attrib["port"])
            
            if len(players) == 0:
                continue

            content += f"\n{'' if passwordProtected else '*'}*{serverName} ({bigip(ip)}:{port})*{'' if passwordProtected else '*'}: {len(players)} player{'s' if len(players) > 1 else ''} - {convertAddonIdToName(currentTrack) if currentTrack != '' else 'None'}:\n"

            for player in players:

                username = player.attrib["username"]
                countrycode = player.attrib["country-code"]

                content += f"{flagconverter(countrycode)} {username}\n"

            if not (currentPlayers - len(players) <= 0):
                content += f"+{currentPlayers - len(players)}\n"

        if content == "":
            content += "No players online!\n"

        content += f"\n###### Last updated: <t:{int(time())}:D> <t:{int(time())}:T>"

        embed = SendableEmbed(
            title = "Online rignt now in STK",
            description = content
        )
        try:
            for i in (await globals.pgconn.fetch("SELECT * FROM lina_conf;")):
                if not i["onlinechannel"]: continue
            
                c: TextChannel = client.get_channel(i["onlinechannel"])
                if i["onlinemessageid"]:
                    try:
                        m: Message  = await c.fetch_message(i["onlinemessageid"])
                        await m.edit(embed=embed)
                    except HTTPError as e:
                        match e.response.status:
                            case 429:
                                log("OnlineChannel", "WARNING! Being rate limited!")
                            case 404:
                                log("OnlineChannel", f"Could not find message {i['onlinemessageid']} for server {i['serverid']}. Sending a new one.")
                                new = await c.send(embed=embed)
                                await globals.pgconn.execute("UPDATE lina_conf SET onlinemessageid = $1 WHERE serverid = $2", new.id, new.server.id)
                            case _:
                                log("OnlineChannel", f"WARNING! Got error code: {e.response.status}")
                else:
                    new = await c.send(embed=embed)
                    await globals.pgconn.execute("UPDATE lina_conf SET onlinemessageid = $1 WHERE serverid = $2", new.id, new.server.id)

                await asyncio.sleep(1)
        except Exception as e:
            log("OnlineChannel", f"Got outer error: {e}")

        await asyncio.sleep(5)
