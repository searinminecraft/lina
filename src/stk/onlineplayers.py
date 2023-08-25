from stk.api import server

import xml.etree.ElementTree as et
from xml.etree.ElementTree import Element

from globals import lastonlinelist

import asyncio


async def onlineloop():

    while True:

        data = await server.getAll()

        lastonlinelist = data

        await asyncio.sleep(5)

