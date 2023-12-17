from stk.http import get


async def getAll():
    return await get('/api/v2/server/get-all')
