from stk.api import user

import globals
import config


async def authenticate(username: str = None, password: str = None):

    if not username:
        username = config.getConfig("username")
    if not password:
        password = config.getConfig("password")

    res = await user.connect(username, password)

    globals.stkToken = res.get('token')
    globals.stkUserId = res.get('userid')
