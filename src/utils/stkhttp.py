"""

For some goddamn reason, i cannot send requests to STK servers, with all python http libraries i used. so,
im forced to use curl. thanks benai for making the api as shitty as possible

"""

import subprocess
import xml.etree.ElementTree as et

class STKError(Exception):
    pass

class ProcessError(Exception):
    pass

def request(method: str, call: str, args: str):

    ret = None

    process = subprocess.run(['curl', '-sX', method, '-d', args, '--user-agent', 'SuperTuxKart/1.4 (Linux)', f'https://online.supertuxkart.net/api/v2/user/{call}'], stdout=subprocess.PIPE)

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
