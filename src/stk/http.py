import aiohttp
import xml.etree.ElementTree as et
from xml.etree.ElementTree import Element
from log import *
import config

import globals

from voltage import __version__ as voltageversion
from version import version

USERAGENT = f"Mozilla/5.0 (compatible; Voltage/{voltageversion}) linaSTK/{version} +https://github.com/searinminecraft/lina"

headers_post = {
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": USERAGENT
}

headers_get = {
    "User-Agent": USERAGENT
}

base_url = "https://online.supertuxkart.net"

class STKHTTPError(Exception):
    pass

async def get(target: str) -> Element:

    async with aiohttp.ClientSession(base_url) as session:

        if config.getConfig("verbose_http"): log('STKHttp', f'Sending GET to {base_url}{target}')

        async with session.get(
                target,
                headers = headers_get
        ) as response: 

            data = et.fromstring(await response.text('utf-8'))

    if data.get("success") == 'no':

        raise STKHTTPError(data.get("info"))

    else: return data

async def post(target: str, authorization: bool = True, **kwargs) -> Element:
    
    credsPayload = f"userid={globals.stkUserId}&token={globals.stkToken}&"

    async with aiohttp.ClientSession(base_url) as session:
        payload = ""

        for key, value in kwargs.items():
            payload += f"{key.replace('_', '-')}={value}&"

        if authorization == True:
            if config.getConfig("verbose_http"): log('STKHttp', f'Sending POST to {base_url}{target} with args {credsPayload}{payload}')
            async with session.post(
                target,
                data = credsPayload + payload,
                headers = headers_post
            ) as response:

                data = et.fromstring(await response.text('utf-8'))
        else:
            
            if config.getConfig("verbose_http"): log('STKHttp', f'Sending POST to {base_url}{target} with args {payload}')
            async with session.post(
                target,
                data = payload,
                headers = headers_post
            ) as response:

                data = et.fromstring(await response.text('utf-8'))


    if data.get("success") == 'no':

        raise STKHTTPError(data.get("info"))

    else: return data

