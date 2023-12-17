import globals

from voltage.ext.commands import CommandsClient
from log import log
import random
from asyncio import sleep, CancelledError
from datetime import datetime


async def statusloop():

    client: CommandsClient = globals.client

    while True:

        now = datetime.now()

        try:
            if now.day == 12 and now.month == 10:
                await client.set_status("Happy birthday searingmoonlight ^w^")
            else:
                statuses = open('statuses.txt').read().splitlines()
                stkseencount = await globals.pgconn.fetchrow(
                    "SELECT COUNT(username) from stk_seen;")

                status = str(random.choice(statuses)).format(
                    prefix=client.prefix,
                    stkseen_amt=stkseencount["count"],
                    online=len(globals.onlinePlayers),
                    users=len(client.users),
                    servers=len(client.servers),
                    version=globals.version
                )

                await client.set_status(status)

            await sleep(60)
        except CancelledError:
            break
        except Exception as e:
            log("Status",
                f"Unable to set status: {e.__class__.__name__}: {e}. "
                "Retrying in 5 seconds.")
            await sleep(5)
