from starlette.responses import JSONResponse
from starlette.requests import Request
from starlette.routing import Route

from api.database import get_user_and_validate_session, get_user_achievement_raw, get_user_achievement_grouped, get_user_achieved_list
from api.misc import get_standard_response, convert_datetime

async def api_achievement_raw(request: Request):
    user, user_profile, error = await get_user_and_validate_session(request)
    if error:
        return error
    
    response_data, completed_ach = await get_standard_response(user, user_profile)
    response_data['message'] = "Success."
    response_data['data'] = {
            "achievements": await get_user_achievement_raw(user['pk'])
        }
    response_data = convert_datetime(response_data)
    return JSONResponse(response_data)

async def api_achievement_grouped(request: Request):
    user, user_profile, error = await get_user_and_validate_session(request)
    if error:
        return error
    
    response_data, completed_ach = await get_standard_response(user, user_profile)
    response_data['message'] = "Success."
    response_data['data'] = {
            "achievements": await get_user_achievement_grouped(user['pk'])
        }
    response_data = convert_datetime(response_data)
    return JSONResponse(response_data)

async def api_prologue_achieve(request: Request):
    user, user_profile, error = await get_user_and_validate_session(request)
    if error:
        return error
    achievement_queue = {}
    achievement_queue['66'] = 1  # Prologue Clear
    response_data, completed_ach = await get_standard_response(user, user_profile, achievement_list=achievement_queue)
    response_data['message'] = "Success."

    response_data['data'] = {
        "achievedList": await get_user_achieved_list(user['pk'], completed_ach)
    }

    response_data = convert_datetime(response_data)
    return JSONResponse(response_data)

async def api_credit_achieve(request: Request):
    user, user_profile, error = await get_user_and_validate_session(request)
    if error:
        return error
    achievement_queue = {}
    achievement_queue['1'] = 1  # Credit Clear
    response_data, completed_ach = await get_standard_response(user, user_profile, achievement_list=achievement_queue)
    response_data['message'] = "Success."

    response_data['data'] = {
        "achievedList": await get_user_achieved_list(user['pk'], completed_ach)
    }

    response_data = convert_datetime(response_data)
    return JSONResponse(response_data)

route = [
    Route("/api/achievement/raw", api_achievement_raw, methods=["GET"]),
    Route("/api/achievement/grouped", api_achievement_grouped, methods=["GET"]),
    Route("/api/prologue/achieve", api_prologue_achieve, methods=["POST"]),
    Route("/api/credit/achieve", api_credit_achieve, methods=["POST"]),
]