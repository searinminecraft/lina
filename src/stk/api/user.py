from stk.http import *

from globals import stkUserId

async def poll():

    return await post('/api/v2/user/poll')

async def connect(username: str, password: str):

    return await post('/api/v2/user/connect',
                      False,
                      username = username,
                      password = password,
                      save_session = 'true')

async def savedSession():

    return await post('/api/v2/user/saved-session')

async def getFriendsList(visitingid: int):

    return await post('/api/v2/user/get-friends-list', visitingid = visitingid)

async def getAchievements(visitingid: int):

    return await post('/api/v2/user/get-achievements', visitingid = visitingid)

async def getAddonVote(addonid: str):

    return await post('/api/v2/user/get-addon-vote', addonid = addonid),

async def setAddonVote(addonid: str, rating: int):

    return await post('/api/v2/user/set-addon-vote',
                      addonid = addonid,
                      rating = rating)

async def clientQuit():

    return await post('/api/v2/user/client-quit')

async def disconnect():

    return await post('/api/v2/user/disconnect')

async def achieving(achievementid: list):

    data = "%20".join(achievementid)

    return await post('/api/v2/user/achieving',
                      achievementid = data),

async def friendRequest(friendid: int):

    return await post('/api/v2/user/friend-request', friendid = friendid)

async def acceptFriendRequest(friendid: int):

    return await post('/api/v2/user/accept-friend-request', friendid = friendid)

async def declineFriendRequest(friendid: int):

    return await post('/api/v2/user/decline-friend-request', friendid = friendid)

async def cancelFriendRequest(friendid: int):

    return await post('/api/v2/user/cancel-friend-request', friendid = friendid)

async def removeFriend(friendid: int):

    return await post('/api/v2/user/remove-friend', friendid = friendid)

async def userSearch(query: str):

    return await post('/api/v2/user/user-search', search_string = query)

async def register(
        username: str,
        password: str,
        password_confirm: str,
        email: str,
        realname: str
        ):

    return await post('/api/v2/user/register',
                      False,
                      username = username,
                      password = password,
                      password_confirm = password_confirm,
                      email = email.replace('@', '%40'),
                      realname = realname,
                      terms = 'on')
        
async def recover(username: str, email: str):

    return await post('/api/v2/user/recover',
                      False,
                      username = username,
                      email = email.replace('@', '%40')
                      )

async def changePassword(
        current: str,
        new1: str,
        new2: str
        ):

    return await post('/api/v2/user/change-password',
                      False,
                      userid = stkUserId,
                      new1 = new1,
                      new2 = new2)

async def getRanking(id: int):

    return await post('/api/v2/user/get-ranking', id = id)

async def topPlayers():

    return await post('/api/v2/user/top-players')

async def changeEmail(newEmail: str):

    return await post('/api/v2/user/change-email', new_email = newEmail.replace('@', '%40'))
