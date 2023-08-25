from voltage.ext.commands import CommandsClient
from voltage import (
    SendableEmbed,
    Message
)
import globals

globals.init()

from stk import authentication
from stk.api.user import clientQuit, disconnect
from stk.http import STKHTTPError
from stk.polling import poll
from stk.onlineloop import onlineloop
from log import log
import config
from version import version

import asyncio
import asyncpg
import traceback
import sys

client = globals.client = CommandsClient(config.getConfig('prefix'))

@client.listen('ready')
async def on_ready():

    import os

    try:
        log('Auth', f"Attempting to authenticate STK account {globals.username}")
        await authentication.authenticate(globals.username, globals.password)
    except STKHTTPError as e:
        log('Auth', f'Unable to authenticate: {e}')
        sys.exit(1)

    log('Auth', f'Successfully logged in as {globals.username}!')

    try:
        log("DB", f"Connecting to {config.getConfig('postgres_conn')}")
        globals.pgconn = await asyncpg.connect(config.getConfig('postgres_conn'))
    except Exception as e:
        log("DB", f"Unable to connect! {e.__class__.__name__}: {e}")
    else:
        log("DB", f"Connected to {config.getConfig('postgres_conn')}!")
        globals.prepared_select = await globals.pgconn.prepare(
"""
SELECT username, LOWER(country) AS country, date, server_name, LOWER(server_country) AS server_country FROM stk_seen2 WHERE
username ILIKE $1 GROUP BY username FETCH FIRST 1 ROW ONLY;
"""
)

        globals.prepared_addc = await globals.pgconn.prepare(
"""
INSERT INTO stk_seen2 (username, date, server_name, server_country) VALUES ($1, now() at time zone 'utc', $2, lower($3))
ON CONFLICT (username) DO UPDATE SET date = now() at time zone 'utc', server_name = $2, server_country = lower($3);
"""
)

        globals.prepared_add = await globals.pgconn.prepare(
"""
INSERT INTO stk_seen2 (username, country, date, server_name, server_country) VALUES ($1, lower($2), now() at time zone 'utc', $3, lower($4))
ON CONFLICT (username) DO UPDATE SET country = lower($2), date = now() at time zone 'utc', server_name = $3, server_country = lower($4);
"""
)
        globals.prepared_ptrack_get = await globals.pgconn.prepare("SELECT id FROM lina_ptrack;")
        globals.prepared_ptrack_query = await globals.pgconn.prepare("SELECT usernames FROM lina_ptrack where id = $1;")

    for file in os.listdir('src/cogs'):
        if file.endswith('.py'):
            try:
                client.add_extension(f'cogs.{file[:-3]}')
                log('Init', f"Loaded {file}")
            except Exception as e:
                log('Init', f"Error loading {file}: {e.__class__.__name__}: {e}")
                log('Init', traceback.format_exc())

    splash = f"""
                           .'
                     ,,.. ..,'
               .,:lloo',;',',,'
           .;cOXXKKKXd:.;'.'.,,
         c0KXK0000000k:::'.     .'
        l0KXK00OO00000l:;        .'
        k0d;,,,,o0KKKK0oc,..ccc:;.....      linaSTK version {version}
        xK:,',',cO00000kcc;.....    .,      Logged in as: {config.getConfig("username")}@stk
        :Kk,:c...;xOKKOOOc:,.   .   .,
         .Oxdx'....dOdcOXdc:;.. .... .
           0,,......'..,Ox,odlc;'....       Avatar and artwork made by dapdap
          .0:.........:O0;O00d ....
         ,OXNkl;...,lxNWWXN000Ol,
        cKWWWWNXK0OdO0NWWWWNK0k od
        kXWWWo'..,dOd;',;:ld000xxd
         oXNo;,..,ddd'.....,,l0k;
          ,d':'.':ooo'....':''x
          ;';,...ccoo.....':'.,.
         :.,;....'lo',.....;,..:
    """

    for i in splash.splitlines():
        log("Bot", i)

    global pollLoop
    global onlineLoop
    
    pollLoop = asyncio.create_task(poll())
    onlineLoop = asyncio.create_task(onlineloop())


@client.error('message')
async def on_error(error: Exception, message: Message):

    log("ErrorHandler", f"Exception occured: {error.__class__.__name__}: {error}")
    traceback.print_exc()

    if isinstance(error, STKHTTPError):
        return await message.reply(embed=SendableEmbed(
            description = f"STK server returned error: {error}",
            color = globals.accentcolor
        ))

async def terminate():
    pollLoop.cancel()
    onlineLoop.cancel()

while True:
    try:
        client.run(config.getConfig('token'))
        asyncio.run(terminate())
    except KeyboardInterrupt:
        log("Bot", "Interrupt.")
        asyncio.run(terminate())
        asyncio.run(clientQuit())
        asyncio.run(disconnect())
        sys.exit(1)
    except Exception as e:
        log("Init", f"Error occured! {e.__class__.__name__}: {e}")
