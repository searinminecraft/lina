from stk.api import server
import globals
from stk.playertrack import triggerDiff
import config
from log import *
import asyncio
import asyncpg

async def onlineloop():

    conn = await asyncpg.connect(config.getConfig("postgres_conn"))
   

    while True:
        try:
            data = await server.getAll()

            globals.lastonlinelist = data

            await triggerDiff(globals.lastonlinelist)
            await asyncio.sleep(config.getConfig("server_fetch_interval"))
        except Exception as e:
            log("OnlineLoop", f"Error occured! {e.__class__.__name__}: {e}")
        except asyncio.CancelledError:
            break

