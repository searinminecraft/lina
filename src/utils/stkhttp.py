import xml.etree.ElementTree as et
from .log import *
from dotenv import dotenv_values, load_dotenv
import aiohttp

class STKError(Exception):
    pass

base_url = 'https://online.supertuxkart.net'

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "SuperTuxKart/1.4 (Linux)"
}

async def request(call: str, args: str):

    ret = None

    async with aiohttp.ClientSession(base_url) as session:
        log('STKHttp', f'Sending {args} to {base_url}/api/v2/user/{call}', color.BLUE)
        async with session.post(f'/api/v2/user/{call}', data=args, headers=headers) as req:
            resp = await req.text('utf-8')
            
    data = et.fromstring(resp)

    if data.get('success') == 'no':
        raise STKError(data.get('info'))


    match call:
        case 'poll':
                    
            ret = data.attrib

        case 'saved-session':

            ret = data.attrib

        case 'get-friends-list':
            out = {}

            for i in data.find('friends'):
                out[i[0].get('user_name')] = {**dict(i.attrib), **dict(i[0].attrib)}

            ret = out

        case 'get-ranking':
                    
            ret = data.attrib

        case 'top-players':
            out = {}

            for i in data[0]:

                out[i.get('username')] = {**dict(i.attrib)}

            ret = out

        case 'user-search':
            out = {}

            for i in data[0]:
                out[i.get('user_name')] = {**dict(i.attrib)}

            ret = out
        case _:

            ret = data.attrib


    return ret
