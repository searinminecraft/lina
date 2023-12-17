from stk.api import user
from stk import authentication
from stk.http import STKHTTPError

import asyncio
from log import log


async def poll():

    while True:
        try:
            await user.poll()
            await asyncio.sleep(120)
        except STKHTTPError:
            log("Polling",
                "Poll request failed (session invalidated?). Reauthenticating."
                )
            await authentication.authenticate()
        except asyncio.CancelledError:
            break
        except Exception as e:
            log("Polling",
                "Poll request failed due to exception:"
                f"{e.__class__.__name__}: {e}")
