import xml.etree.ElementTree as et
import asyncio

import globals
from config import getConfig
from log import log
from utils.flagconverter import flagconverter
from utils.bigip import bigip

from voltage.ext.commands import CommandsClient
from voltage import DMChannel, SendableEmbed

prevTree: et.Element = None
onlinePlayers = {}


async def ptrack_NotifyUserJoin(userId, username, country, server, serverCountry):

    client: CommandsClient = globals.client

    try:
        dm = await client.http.open_dm(userId)
        channel = DMChannel(dm, client.cache)

        await channel.send(
            f"$% {flagconverter(country)} {username} joined a server %$",
            embed=SendableEmbed(
                title="STK Player Tracker",
                description=f"""{flagconverter(country)} {username} joined a server

Server: {flagconverter(serverCountry)} {server}
            """,
                color=globals.accentcolor,
                icon_url=getConfig("embed_icon")
            ))

    except Exception as e:
        log("ptrackNotify",
            f"Unable to notify user {userId}: {e.__class__.__name__}: {e}")


async def ptrack_NotifyUserLeave(userId, username, country, server, serverCountry):

    client: CommandsClient = globals.client

    try:
        dm = await client.http.open_dm(userId)
        channel = DMChannel(dm, client.cache)

        await channel.send(
            f"$% {flagconverter(country)} {username} left %$",
            embed=SendableEmbed(
                title="STK Player Tracker",
                description=f"""{flagconverter(country)} {username} left

Server: {flagconverter(serverCountry)} {server}
            """,
                color=globals.accentcolor,
                icon_url=getConfig("embed_icon")
            ))

    except Exception as e:
        log("ptrackNotify",
            f"Unable to notify user {userId}: {e.__class__.__name__}: {e}")


async def triggerDiff(tree: et.Element):
    global prevTree
    global onlinePlayers

    if not prevTree:
        prevTree = tree

    ids_old = set(int(x[0].attrib["id"]) for x in prevTree[0])
    ids_new = set(int(x[0].attrib["id"]) for x in tree[0])

    srvCreated = ids_new.difference(ids_old)
    srvDeleted = ids_old.difference(ids_new)

    playersToInsert = []
    playersToInsertnocc = []
    xmlServersCreated = []
    xmlServersDeleted = []

    for i in range(len(tree[0])):

        _id = int(tree[0][i][0].attrib["id"])

        if _id in srvCreated:

            log("PlayerTrack", "New server created: %s (%s) with id %d and address %s:%d" % (
                tree[0][i][0].attrib['name'],
                tree[0][i][0].attrib['country_code'],
                int(tree[0][i][0].attrib['id']),
                bigip(int(tree[0][i][0].attrib['ip'])),
                int(tree[0][i][0].attrib['port'])
                ))

            playersJoined = tree[0][i][1]

            for player in playersJoined:

                username = player.attrib["username"]
                country = player.attrib["country-code"]
                serverInfo = tree[0][i][0]
                serverName = serverInfo.attrib["name"]
                serverCountry = serverInfo.attrib['country_code']
                playersToInsert.append((username, country,
                                        serverName, serverCountry))

                if username not in onlinePlayers:
                    onlinePlayers[username] = serverInfo

            xmlServersCreated.append(tree[0][i])

    for i in range(len(prevTree[0])):

        _id = int(prevTree[0][i][0].attrib["id"])

        if _id in srvDeleted:

            log("PlayerTrack", "Server deleted: %s (%s) with id %d and address %s:%d" % (
                prevTree[0][i][0].attrib['name'],
                prevTree[0][i][0].attrib['country_code'],
                int(prevTree[0][i][0].attrib['id']),
                bigip(int(prevTree[0][i][0].attrib['ip'])),
                int(prevTree[0][i][0].attrib['port'])
                ))

            xmlServersDeleted.append(tree[0][i])

            playersLeft = prevTree[0][i][1]

            for player in playersLeft:
                username = player.attrib['username']
                serverInfo = prevTree[0][i][0]
                serverName = serverInfo.attrib['name']
                serverCountry = serverInfo.attrib['country_code']

                playersToInsertnocc.append((username,
                                            serverName,
                                            serverCountry))
                if username in onlinePlayers:
                    del onlinePlayers[username]

    # Some optimization procedure stuff
    pairs = {}
    offset = 0

    for i in range(min(len(tree[0]), len(prevTree[0]))):
        _id_next = int(tree[0][i][0].attrib['id'])

        try:

            _id_prev = int(prevTree[0][i + offset][0].attrib['id'])

        except IndexError:
            log("PlayerTrack",
                "Bad index: prevTree[0][%s][0] is out of boundaries, offset %s, i=%s, len(tree[0]) = %s, len(prevTree[0] = %s)" % (
                    i + offset,
                    offset,
                    i,
                    len(tree[0]),
                    len(prevTree[0])
                ))
            continue

        if _id_next == _id_prev:
            pairs[tree[0][i]] = prevTree[0][i + offset]
        elif _id_next in srvCreated:
            offset -= 1
        elif len(tree[0]) != len(prevTree[0]):
            while _id_prev in srvDeleted:
                _id_prev = int(prevTree[0][i + offset][0].attrib['id'])
                if _id_prev in srvDeleted:
                    offset += 1
                elif _id_prev == _id_next:
                    pairs[tree[0][i]] = prevTree[0][i + offset]
                    break
                else:
                    log("PlayerTrack",
                        "Failed to find an offset at _id_next %s" % _id_next)

    for pair in pairs:
        oldServerInfo = pairs[pair][0]
        oldServerPlayers = pairs[pair][1]
        serverInfo = pair[0]
        serverPlayers = pair[1]

        if serverInfo.attrib['id'] != oldServerInfo.attrib['id']:
            log("PlayerTrack", "Server IDs don't match: %s %s" % (
                serverInfo.attrib['id'],
                oldServerInfo.attrib['id']
                ))
            continue

        serverCTrack = None
        oldserverCTrack = None
        if "current_track" in serverInfo.attrib:
            serverCTrack = serverInfo.attrib["current_track"]
        if "current_track" in oldServerInfo.attrib:
            oldserverCTrack = oldServerInfo.attrib["current_track"]

            if serverCTrack != oldserverCTrack:
                if not oldserverCTrack:
                    log("PlayerTrack", "Stub: Game started at %s %s - %s" % (
                        serverInfo.attrib['name'],
                        serverInfo.attrib['id'],
                        serverCTrack
                    ))
                elif not serverCTrack:
                    log("PlayerTrack",
                        "Stub: Game ended at %s %s" % (
                            serverInfo.attrib['name'],
                            serverInfo.attrib['id']
                        ))
        diff_attrib = set()
        for attrib in ('max_players',
                       'game_mode',
                       'difficulty'):
            if serverInfo.attrib[attrib] != oldServerInfo.attrib[attrib]:
                diff_attrib.add(attrib)

        if diff_attrib:
            log("PlayerTrack", "Stub: Config difference detected at %s: %s"
                % (serverInfo.attrib['name'], diff_attrib))

        playersNew = set(str(x.attrib['username']) for x in serverPlayers)
        playersOld = set(str(x.attrib['username']) for x in oldServerPlayers)
        playersJoined = playersNew.difference(playersOld)
        playersLeft = playersOld.difference(playersNew)

        for i in range(len(serverPlayers)):
            username = serverPlayers[i].attrib['username']
            userCountryCode = serverPlayers[i].attrib['country-code'].lower() if 'country-code' in serverPlayers[i].attrib else ''

            if username in playersJoined:
                if 'country-code' in serverPlayers[i].attrib:

                    serverName = serverInfo.attrib['name']
                    serverCountry = serverInfo.attrib['country_code']

                    playersToInsert.append((
                        username,
                        userCountryCode,
                        serverName,
                        serverCountry
                        ))

                    onlinePlayers[username] = serverInfo

                for i in await globals.prepared_ptrack_get.fetch():

                    id = i["id"]

                    data = await globals.prepared_ptrack_query.fetchrow(id)

                    if data is None:
                        continue

                    if username in data["usernames"]:
                        asyncio.create_task(
                            ptrack_NotifyUserJoin(id, username,
                                                  userCountryCode,
                                                  serverName, serverCountry))

        for i in range(len(oldServerPlayers)):
            if i >= len(oldServerPlayers):
                log("PlayerTrack",
                    "Impossible happened: iteration %s is over oldServerPlayers length: %s"
                    % (i, len(oldServerPlayers)))
                continue

            username = oldServerPlayers[i].attrib['username']
            userCountryCode = oldServerPlayers[i].attrib['country-code']

            if username in playersLeft:
                if 'country-code' in oldServerPlayers[i].attrib:

                    serverName = oldServerInfo.attrib['name']
                    serverCountry = oldServerInfo.attrib['country_code']

                    playersToInsert.append((
                        username,
                        userCountryCode,
                        serverName,
                        serverCountry
                        ))

                    if username in onlinePlayers:
                        del onlinePlayers[username]

                for i in await globals.prepared_ptrack_get.fetch():

                    id = i["id"]

                    data = await globals.prepared_ptrack_query.fetchrow(id)

                    if data is None:
                        continue

                    if username in data["usernames"]:
                        asyncio.create_task(ptrack_NotifyUserLeave(
                            id, username,
                            userCountryCode, serverName,
                            serverCountry))

        if len(oldServerPlayers) != len(serverPlayers):
            log("PlayerTrack",
                f"Stub: Server {serverName} became full or free")

    try:
        if playersToInsertnocc:
            await globals.prepared_addc.executemany(playersToInsertnocc)
        if playersToInsert:
            await globals.prepared_add.executemany(playersToInsert)

        playersToInsert.clear()
        playersToInsertnocc.clear()
    except Exception as e:
        log("PlayerTrack",
            f"Unable to save player info to DB: {e.__class__.__name__}: {e}")

    if getConfig("debug_noonline"):
        log("Debug", "not saving online players to globals")
        pass
    else:
        globals.onlinePlayers = onlinePlayers

    prevTree = tree
    globals.onlinePlayers = onlinePlayers

    prevTree = tree
