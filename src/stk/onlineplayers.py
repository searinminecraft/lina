from stk.api import server
import globals
import asyncio

async def onlineloop():
    while True:
        data = await server.getAll()
        globals.lastonlinelist = data
        await asyncio.sleep(5)
