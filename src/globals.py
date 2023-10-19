import config
import datetime

def init():
    global username
    global password
    global stkToken
    global stkUserId
    global accentcolor
    global lastonlinelist
    global client

    global pgconn
   
    global prepared_add
    global prepared_addc
    global prepared_ptrack_upd
    global prepared_ptrack_get
    global prepared_ptrack_query
    global prepared_select

    global onlinePlayers

    global startTime

    username = config.getConfig('username')
    password = config.getConfig('password')
    accentcolor = config.getConfig('accentcolor')
    stkUserId = None
    stkToken = None
    lastonlinelist = None
    client = None
    pgconn = None
    prepared_ptrack_query = None
    prepared_ptrack_upd = None
    prepared_ptrack_get = None
    prepared_add = None
    prepared_addc = None
    prepared_select = None
    onlinePlayers = {}
    startTime = datetime.datetime.now()
