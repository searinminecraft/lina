from stk.api import user

import globals
import config

async def authenticate(username: str = None, password: str =  None):

    if username is None: username = config.getConfig("username")
    if password is None: password = config.getConfig("password")

    res = await user.connect(username, password)

    globals.stkToken = res.get('token')
    globals.stkUserId = res.get('userid')
