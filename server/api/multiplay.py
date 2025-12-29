from starlette.responses import JSONResponse
from starlette.requests import Request
from starlette.routing import Route
import copy

from api.database import player_database, get_user_and_validate_session
from api.misc import get_standard_response
from api.cache import load_rooms

async def multiplay_room(request: Request):
    user, user_profile, error = await get_user_and_validate_session(request)
    if error:
        return error

    await load_rooms()
    from api.cache import ROOMS
    rooms = copy.deepcopy(ROOMS)
    rooms = rooms['data']

    room_list = []
    for room_id, room_data in rooms.items():
        nickname_list = [room_data['host_userprofile']['nickname']]
        if room_data['opponent_userprofile']:
            nickname_list.append(room_data['opponent_userprofile']['nickname'])
        
        room_list.append(
            {"roomCode": room_data['room_key'], "nicknames": nickname_list}
        )
    
    response_data, completed_ach = await get_standard_response(user, user_profile)
    response_data['message'] = "Success."
    response_data['data'] = {
        "rooms": room_list
    }

    return JSONResponse(response_data)

route = [
    Route("/api/multiplay/rooms", multiplay_room, methods=["GET"]),
]