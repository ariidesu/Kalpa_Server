from starlette.responses import JSONResponse
from starlette.requests import Request
from starlette.routing import Route
from datetime import datetime

from api.database import player_database, userProfiles, userFriends, get_user_and_validate_session, get_user_profile_by_uid, get_user_friend_pair

from api.misc import get_standard_response, convert_datetime

async def api_friend_search(request: Request):
    user, user_profile, error = await get_user_and_validate_session(request)
    if error:
        return error

    user_uid = request.path_params['user_uid']
    if not user_uid:
        message = "User UID is required."
        status = 400
        data = {}

    else:
        target_user_profile = await get_user_profile_by_uid(user_uid)
        if not target_user_profile:
            message = "Success."
            status = 200
            data = {}

        else:
            message = "Success."
            status = 200
            data = {
                "searchedUser": target_user_profile
            }
    
    json_data, completed_ach = await get_standard_response(user, user_profile)
    json_data['message'] = message
    json_data['data'] = data
    return JSONResponse(json_data, status_code=status)

async def friend_change_newfriendrequest(request: Request):
    user, user_profile, error = await get_user_and_validate_session(request)
    if error:
        return error
    
    query = userProfiles.update().where(userProfiles.c.pk == user['pk']).values(newFriendRequest=0)
    await player_database.execute(query)

    json_data, completed_ach = await get_standard_response(user, user_profile)
    json_data['message'] = "Success."
    json_data['data'] = {}
    json_data = convert_datetime(json_data)
    return JSONResponse(json_data, status_code=200)

async def friend_request_send(request: Request):
    user, user_profile, error = await get_user_and_validate_session(request)
    if error:
        return
    
    form = await request.form()
    friend_user_pk = int(form.get('friendUserPk', 0))
    data = {}

    if not friend_user_pk:
        message = "friendUserPk is required."
        status = 400
    else:
        user_query = userProfiles.select().where(userProfiles.c.UserPk == friend_user_pk)
        friend_user = await player_database.fetch_one(user_query)
        if not friend_user:
            message = "User not found."
            status = 400
        else:
            user_friend = await get_user_friend_pair(user['pk'], friend_user_pk)
            if user_friend:
                if user_friend['InviterState'] == 1:
                    message = "You are already friends."
                    status = 400
                elif user_friend['InviteeState'] in [2, 3]:
                    message = "Friend request already sent and is pending."
                    status = 400
                else:
                    if user_friend['InviterPk'] == user['pk']:
                        query = userFriends.update().where((userFriends.c.InviterPk == user['pk']) & (userFriends.c.InviteePk == friend_user_pk)).values(InviterState=2, InviteeState=3, updatedAt=datetime.utcnow())
                    else:
                        query = userFriends.update().where((userFriends.c.InviterPk == friend_user_pk) & (userFriends.c.InviteePk == user['pk'])).values(InviterState=3, InviteeState=2, updatedAt=datetime.utcnow())
                    await player_database.execute(query)
                    query = userProfiles.update().where(userProfiles.c.UserPk == friend_user_pk).values(newFriendRequest=userProfiles.c.newFriendRequest + 1)
                    await player_database.execute(query)
                    message = "Success."
                    status = 200
            else:
                query = userFriends.insert().values(InviterPk=user['pk'], InviteePk=friend_user_pk, InviterState=2, InviteeState=3, createdAt=datetime.utcnow(), updatedAt=datetime.utcnow())
                await player_database.execute(query)
                query = userProfiles.update().where(userProfiles.c.UserPk == friend_user_pk).values(newFriendRequest=userProfiles.c.newFriendRequest + 1)
                await player_database.execute(query)
                message = "Success."
                status = 200

    json_data, completed_ach = await get_standard_response(user, user_profile)
    json_data['message'] = message
    json_data['data'] = data
    json_data = convert_datetime(json_data)
    return JSONResponse(json_data, status_code=status)

async def friend_request_accept(request: Request):
    user, user_profile, error = await get_user_and_validate_session(request)
    if error:
        return error
    
    form = await request.form()
    friend_user_pk = int(form.get('friendUserPk', 0))
    data = {}

    if not friend_user_pk:
        message = "friendUserPk is required."
        status = 400
    else:
        user_query = userProfiles.select().where(userProfiles.c.UserPk == friend_user_pk)
        friend_user = await player_database.fetch_one(user_query)
        if not friend_user:
            message = "User not found."
            status = 400
        else:
            user_friend = await get_user_friend_pair(user['pk'], friend_user_pk)
            valid_invite = user_friend and ((user_friend['InviterPk'] == friend_user_pk and user_friend['InviteeState'] == 3) or (user_friend['InviterPk'] == user['pk'] and user_friend['InviteeState'] == 2))
            if not valid_invite:
                message = "No pending friend request from this user."
                status = 400
            else:
                if user_friend['InviterPk'] == user['pk']:
                    query = userFriends.update().where((userFriends.c.InviterPk == user['pk']) & (userFriends.c.InviteePk == friend_user_pk)).values(InviterState=1, InviteeState=1, updatedAt=datetime.utcnow())
                else:
                    query = userFriends.update().where((userFriends.c.InviterPk == friend_user_pk) & (userFriends.c.InviteePk == user['pk'])).values(InviterState=1, InviteeState=1, updatedAt=datetime.utcnow())
                await player_database.execute(query)
                message = "Success."
                status = 200

    json_data, completed_ach = await get_standard_response(user, user_profile)
    json_data['message'] = message
    json_data['data'] = data
    json_data = convert_datetime(json_data)
    return JSONResponse(json_data, status_code=status)

async def friend_request_reject(request: Request):
    user, user_profile, error = await get_user_and_validate_session(request)
    if error:
        return error
    
    form = await request.form()
    friend_user_pk = int(form.get('friendUserPk', 0))
    data = {}

    if not friend_user_pk:
        message = "friendUserPk is required."
        status = 400
    else:
        user_query = userProfiles.select().where(userProfiles.c.UserPk == friend_user_pk)
        friend_user = await player_database.fetch_one(user_query)
        if not friend_user:
            message = "User not found."
            status = 400
        else:
            user_friend = await get_user_friend_pair(user['pk'], friend_user_pk)
            valid_invite = user_friend and ((user_friend['InviterPk'] == friend_user_pk and user_friend['InviteeState'] == 3) or (user_friend['InviterPk'] == user['pk'] and user_friend['InviteeState'] == 2))
            if not valid_invite:
                message = "No pending friend request from this user."
                status = 400
            else:
                if user_friend['InviterPk'] == user['pk']:
                    query = userFriends.update().where((userFriends.c.InviterPk == user['pk']) & (userFriends.c.InviteePk == friend_user_pk)).values(InviterState=4, InviteeState=4, updatedAt=datetime.utcnow())
                else:
                    query = userFriends.update().where((userFriends.c.InviterPk == friend_user_pk) & (userFriends.c.InviteePk == user['pk'])).values(InviterState=4, InviteeState=4, updatedAt=datetime.utcnow())
                await player_database.execute(query)
                message = "Success."
                status = 200

    json_data, completed_ach = await get_standard_response(user, user_profile)
    json_data['message'] = message
    json_data['data'] = data
    json_data = convert_datetime(json_data)
    return JSONResponse(json_data, status_code=status)

async def friend_delete(request: Request):
    user, user_profile, error = await get_user_and_validate_session(request)
    if error:
        return error
    
    form = await request.form()
    friend_user_pk = int(form.get('friendUserPk', 0))
    data = {}

    if not friend_user_pk:
        message = "friendUserPk is required."
        status = 400
    else:
        user_query = userProfiles.select().where(userProfiles.c.UserPk == friend_user_pk)
        friend_user = await player_database.fetch_one(user_query)
        if not friend_user:
            message = "User not found."
            status = 400
        else:
            user_friend = await get_user_friend_pair(user['pk'], friend_user_pk)
            is_friend = user_friend and (user_friend['InviterState'] == 1 and user_friend['InviteeState'] == 1)
            if not is_friend:
                message = "You are not a friend with this user."
                status = 400
            else:
                if user_friend['InviterPk'] == user['pk']:
                    query = userFriends.update().where((userFriends.c.InviterPk == user['pk']) & (userFriends.c.InviteePk == friend_user_pk)).values(InviterState=4, InviteeState=4, updatedAt=datetime.utcnow())
                else:
                    query = userFriends.update().where((userFriends.c.InviterPk == friend_user_pk) & (userFriends.c.InviteePk == user['pk'])).values(InviterState=4, InviteeState=4, updatedAt=datetime.utcnow())
                await player_database.execute(query)
                message = "Success."
                status = 200

    json_data, completed_ach = await get_standard_response(user, user_profile)
    json_data['message'] = message
    json_data['data'] = data
    json_data = convert_datetime(json_data)
    return JSONResponse(json_data, status_code=status)

route = [
    Route("/api/friend/search/{user_uid}", api_friend_search, methods=["GET"]),
    Route("/api/friend/change/newfriendrequest", friend_change_newfriendrequest, methods=["POST"]),
    Route("/api/friend/request/send", friend_request_send, methods=["POST"]),
    Route("/api/friend/request/accept", friend_request_accept, methods=["POST"]),
    Route("/api/friend/request/reject", friend_request_reject, methods=["POST"]),
    Route("/api/friend/delete", friend_delete, methods=["POST"])
]