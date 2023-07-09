"""

A reimplementation of NobWow's stk-playertrack module for snakebot on Voltage.

This took me so long and a ton of debugging to get working. I hate myself.

"""

import voltage
from voltage.ext import commands

import aiohttp
import asyncio
import asyncpg
import xml.etree.ElementTree as et
from dotenv import dotenv_values, load_dotenv
from utils.log import *

load_dotenv()

accent = dotenv_values()['accent']
postgresql_conn = dotenv_values()['postgresql_conn']

sql_stkseen = """SELECT username, LOWER(country) AS country, date, server_name, LOWER(server_country) AS server_country FROM stk_seen WHERE
username ILIKE $1 GROUP BY username FETCH FIRST 1 ROW ONLY;
"""

sql_recordplayer = """
INSERT INTO stk_seen (username, country, date, server_name, server_country) VALUES ($1, lower($2), now() at time zone 'utc', $3, lower($4))
ON CONFLICT (username) DO UPDATE SET country = lower($2), date = now() at time zone 'utc', server_name = $3, server_country = lower($4);
"""

sqllike_esc = str.maketrans({
    '%': '\\%',
    '_': '\\_',
    '\\': '\\\\'
}) # teamkrash for some reason thinks maketrans means make it transgender lmao

def flagconverter(code: str):
    if code == 'None': return ''
    res = f"{''.join(chr(127397 + ord(str.upper(k))) for k in code)}"
    return res

def setup(client) -> commands.Cog:

    stkutil = commands.Cog(
        name = 'Utilities',
        description = 'Some useful utilities.'
    )

    @stkutil.command('seen', 'See when the STK user last connected to an STK server (only if user pings STK servers')
    async def stk_seen(ctx: commands.CommandContext, user: str = None):
        if user is None:
            return await ctx.reply('Please specify a user.')

        connection = await asyncpg.connect(postgresql_conn)
        prepared_select = await connection.prepare(sql_stkseen)

        user_q = user.translate(sqllike_esc) + "%"
        userdata = await prepared_select.fetchrow(user_q)

        if userdata is None:
            log('STKSeen', f'Player {user} not found in DB')

            return await ctx.reply(embed=voltage.SendableEmbed(
                title = 'We have not seen this player before.',
                description = 'Player was not found in our database.',
                color = accent
            ))
        else:
            log('STKSeen', f'Player {user} found! Result = {userdata["username"]}', color.GREEN)

            return await ctx.reply(embed=voltage.SendableEmbed(
                title = "STK Seen",
                description = f"""## Information for user {flagconverter(str(userdata["country"]))} {userdata["username"]}

* Date last detected: **{str(userdata["date"])} (UTC)**
* Last seen on: {flagconverter(str(userdata["server_country"]))} **{userdata["server_name"]}**""",
                color = accent
            ))

    return stkutil

