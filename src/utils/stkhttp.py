"""

For some goddamn reason, i cannot send requests to STK servers, with all python http libraries i used. so,
im forced to use curl. thanks benai for making the api as shitty as possible

"""

import subprocess
import xml.etree.ElementTree as et
from .log import *
from dotenv import dotenv_values, load_dotenv

class STKError(Exception):
    
    def __init__(self, reason: str):
        self.reason = reason

    pass

class ProcessError(Exception):
    pass

def request(method: str, call: str, args: str):

    load_dotenv()

    cmd = ['curl', '-sX', method, '-d', args, '--user-agent', 'SuperTuxKart/1.4 (Linux)', f'https://online.supertuxkart.net/api/v2/user/{call}'] 

    ret = None

    log('STKHttp', f'Sending {str(cmd[4]).replace(dotenv_values()["stk_token"], "[redacted]" ).replace(dotenv_values()["stk_password"], "[redacted]")} to {cmd[7]}', color.BLUE)

    process = subprocess.run(cmd, stdout=subprocess.PIPE)

    try:
        process.check_returncode()
    except:
        raise ProcessError('Process returned non-zero status')
   
    data = et.fromstring(process.stdout.decode('utf-8'))

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

        case _:

            ret = data.attrib


    return ret
