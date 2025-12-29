from starlette.responses import JSONResponse
from starlette.requests import Request
from starlette.routing import Route

from api.database import player_database, manifest_database, maps, items, userDarkmoon, get_user_and_validate_session, get_user_darkmoon, check_item_entitlement, init_user_darkmoon
from api.templates_norm import DARKMOON_THUMB, DARKMOON_MULTI
from api.misc import convert_datetime, get_standard_response

async def api_darkmoon_all(request: Request):
    user, user_profile, error = await get_user_and_validate_session(request)
    if error:
        return error

    await init_user_darkmoon(user["pk"])

    data = {
        "darkmoonThumb": DARKMOON_THUMB[0],
        "darkmoonMulti": DARKMOON_MULTI[0],
        "nextDarkmoonThumb": DARKMOON_THUMB[1],
        "nextDarkmoonMulti": DARKMOON_MULTI[1],
        "userDarkmoonThumb": await get_user_darkmoon(user["pk"], DARKMOON_THUMB[0]["pk"], is_thumb=1),
        "userDarkmoonMulti": await get_user_darkmoon(user["pk"], DARKMOON_MULTI[0]["pk"], is_thumb=0)
    }

    if data['userDarkmoonThumb']['rerunMapPk1'] is None:
        del data['userDarkmoonThumb']['rerunMapPk1']
    if data['userDarkmoonThumb']['rerunMapPk2'] is None:
        del data['userDarkmoonThumb']['rerunMapPk2']
    if data['userDarkmoonThumb']['rerunMapPk3'] is None:
        del data['userDarkmoonThumb']['rerunMapPk3']
    if data['userDarkmoonMulti']['rerunMapPk1'] is None:
        del data['userDarkmoonMulti']['rerunMapPk1']
    if data['userDarkmoonMulti']['rerunMapPk2'] is None:
        del data['userDarkmoonMulti']['rerunMapPk2']
    if data['userDarkmoonMulti']['rerunMapPk3'] is None:
        del data['userDarkmoonMulti']['rerunMapPk3']

    response_data, completed_ach = await get_standard_response(user, user_profile)
    response_data['message'] = "Success."
    response_data['data'] = data
    response_data = convert_datetime(response_data)

    return JSONResponse(response_data)

async def darkmoon_random_play(request: Request):
    user, user_profile, error = await get_user_and_validate_session(request)
    if error:
        return
    
    from api.templates_norm import METADATA
    item_queue = {}
    data = {}
    item_queue[METADATA['darkmoonRandomPlayCostKey']] = -METADATA['darkmoonRandomPlayCostValue']
    can_pay = await check_item_entitlement(user['pk'], item_queue)
    if not can_pay:
        status = 400
        message = "Can not afford to play."
    else:
        status = 200
        message = "Success."

    response_data, completed_ach = await get_standard_response(user, user_profile, item_list=item_queue)
    response_data['message'] = message
    response_data['data'] = data

    response_data = convert_datetime(response_data)
    return JSONResponse(response_data, status_code=status)

async def darkmoon_receive_achiev_reward(request: Request):
    user, user_profile, error = await get_user_and_validate_session(request)
    if error:
        return

    form = await request.form()
    darkmoon_pk = int(form.get("darkmoonPk", -1))
    is_thumb = int(form.get("isThumb", -1))
    step = int(form.get("step", -1))
    data = {}
    item_queue = {}
    achievement_queue = {}

    if darkmoon_pk == -1 or is_thumb not in (0, 1) or step not in (1, 2, 3):
        message = "Invalid parameters."
        status = 400
    
    else:
        user_darkmoon_query = userDarkmoon.select().where(
            (userDarkmoon.c.UserPk == user['pk']) &
            (userDarkmoon.c.DarkmoonPk == darkmoon_pk) &
            (userDarkmoon.c.isThumb == is_thumb)
        )
        user_darkmoon = await player_database.fetch_one(user_darkmoon_query)
        if not user_darkmoon:
            message = "Darkmoon not opened."
            status = 400
        else:
            clear_config = [0, 1, 3, 10]
            step_state = user_darkmoon['achievReward' + str(step) + 'State']
            if user_darkmoon['clearedStageNum'] + user_darkmoon['specialClearCount'] < clear_config[step] or step_state:
                if step_state:
                    message = "Reward already received."
                    status = 400
                else:
                    message = "Request not completed yet."
                    status = 400
            else:
                from api.templates_norm import DARKMOON_MULTI, DARKMOON_THUMB
                if is_thumb:
                    darkmoon_list = DARKMOON_THUMB
                else:
                    darkmoon_list = DARKMOON_MULTI
                reward = darkmoon_list[0]['achievRewardItems'][step - 1]

                item_queue[reward['key']] = reward['value']
                if reward['key'].startswith("map."):
                    # achievement checking
                    map_pk = int(reward['key'].split(".")[1])
                    map_query = maps.select().where(maps.c.pk == map_pk)
                    map_info = await manifest_database.fetch_one(map_query)
                    map_info = dict(map_info) if map_info else None
                    if map_info:
                        if map_info['mode'] == 6:
                            # cosmos chart unlock
                            achievement_queue['8'] = 1
                        elif map_info['mode'] == 7:
                            # Abyss chart unlock
                            achievement_queue['53'] = 1

                update_query = userDarkmoon.update().where(
                    (userDarkmoon.c.UserPk == user['pk']) &
                    (userDarkmoon.c.DarkmoonPk == darkmoon_pk)
                ).values({
                    'achievReward' + str(step) + 'State': 1
                })
                await player_database.execute(update_query)

                message = "Success."
                status = 200

    response_data, completed_ach = await get_standard_response(user, user_profile, item_list=item_queue, achievement_list=achievement_queue)
    response_data['message'] = message
    response_data['data'] = data

    response_data = convert_datetime(response_data)
    return JSONResponse(response_data, status_code=status)

async def darkmoon_purchase_rerun_map(request: Request):
    user, user_profile, error = await get_user_and_validate_session(request)
    if error:
        return
    
    form = await request.form()
    map_pk = int(form.get("mapPk", -1))

    map_query = maps.select().where(maps.c.pk == map_pk)
    map_info = await manifest_database.fetch_one(map_query)

    item_query = items.select().where(items.c.key == "map." + str(map_pk))
    item_info = await manifest_database.fetch_one(item_query)

    data = {}
    item_queue = {}

    if not map_info or not item_info:
        message = "Map or item does not exist."
        status = 400
    
    else:
        temp_item_queue = {}
        temp_item_queue['map.' + str(map_pk)] = -1
        ownership = await check_item_entitlement(user['pk'], temp_item_queue)
        if ownership:
            message = "Map already owned."
            status = 400
        
        else:
            from api.templates_norm import METADATA
            item_queue[METADATA['darkmoonRerunPurchaseCostKey']] = -METADATA['darkmoonRerunPurchaseCostValue']
            can_pay = await check_item_entitlement(user['pk'], item_queue)
            if not can_pay:
                message = "Can not afford to purchase."
                status = 400
            else:
                item_queue['map.' + str(map_pk)] = 1
                message = "Success."
                status = 200

    response_data, completed_ach = await get_standard_response(user, user_profile, item_list=item_queue)
    response_data['message'] = message
    response_data['data'] = data

    response_data = convert_datetime(response_data)
    return JSONResponse(response_data, status_code=status)

route = [
    Route("/api/darkmoon/all", api_darkmoon_all, methods=["GET"]),
    Route("/api/darkmoon/randomplay", darkmoon_random_play, methods=["POST"]),
    Route("/api/darkmoon/receiveachievreward", darkmoon_receive_achiev_reward, methods=["POST"]),
    Route("/api/darkmoon/purchasererunmap", darkmoon_purchase_rerun_map, methods=["POST"]),
]