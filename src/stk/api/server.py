from stk.http import *

async def getAll():
    
    return await get('/api/v2/server/get-all')
