from starlette.responses import JSONResponse
from starlette.requests import Request
from starlette.routing import Route
from datetime import datetime

from api.database import player_database, manifest_database, userPerformerHurdleMissions, userPerformerLevelRewards, performerHurdleMissions, performerLevels, userPerformerHurdleMissions, get_user_and_validate_session, get_user_performer_hurdle_missions, get_user_item, get_user_performer_level_rewards, add_mail

from api.misc import get_standard_response, convert_datetime

async def performer_level_receive_reward_all(request: Request):
    user, user_profile, error = await get_user_and_validate_session(request)
    if error:
        return error

    user_performer_hurdle_missions = await get_user_performer_hurdle_missions(user["pk"])
    user_performer_level_rewards = await get_user_performer_level_rewards(user["pk"])

    performer_level_query = performerLevels.select()
    performer_levels = await manifest_database.fetch_all(performer_level_query)
    performer_levels = [dict(row) for row in performer_levels]

    user_performer_exp = await get_user_item(user['pk'], 'performerexp')
    user_performer_exp = user_performer_exp['amount'] if user_performer_exp else 0

    item_queue = {}
    cosmic_ticket = []
    granted = False

    for hurdle in user_performer_hurdle_missions:
        if hurdle['state'] == 1:
            update_query = userPerformerHurdleMissions.update().where(
                (userPerformerHurdleMissions.c.pk == hurdle['pk'])
            ).values(
                state=2
            )
            await player_database.execute(update_query)
            
            hurdle_mission_query = performerHurdleMissions.select().where(performerHurdleMissions.c.pk == hurdle['PerformerHurdleMissionPk'])
            hurdle_mission = await manifest_database.fetch_one(hurdle_mission_query)
            reward = hurdle_mission['rewardItem']
            item_queue[reward['key']] = item_queue.get(reward['key'], 0) + reward['value']
            if reward['key'].startswith('cosmicticket.'):
                cosmic_ticket.append(reward)
                await add_mail(user['pk'], "Cosmic Membership Ticket Payment Mail", f"Cosmic Membership Ticket has been issued. Cosmic Membership Ticket is used immediately upon receipt.\n", [reward], [])

    for level in performer_levels:
        exp_required = level['requiredPerformerEXP']
        if user_performer_exp >= exp_required:
            # player have reached this level
            # if does not exist in performer level rewards, create it.
            level_pk = level['pk']
            reward_exist = any(reward['PerformerLevelPk'] == level_pk for reward in user_performer_level_rewards)
            
            if not reward_exist:
                granted = True
                insert_query = userPerformerLevelRewards.insert().values(
                    UserPk=user['pk'],
                    PerformerLevelPk=level_pk,
                    state=2,
                    createdAt=datetime.utcnow(),
                    updatedAt=datetime.utcnow()
                )
                await player_database.execute(insert_query)
                
                reward = level['rewardItem']
                item_queue[reward['key']] = item_queue.get(reward['key'], 0) + reward['value']
                if reward['key'].startswith('cosmicticket.'):
                    cosmic_ticket.append(reward) 
    if granted:
        user_performer_level_rewards = await get_user_performer_level_rewards(user["pk"])

    data = {
        "userPerformerLevelRewards": user_performer_level_rewards,
        "cosmicTicketRewards": cosmic_ticket,
        "duplicatedItemKeys": [],
    }
    
    json_data, completed_ach = await get_standard_response(user, user_profile, item_list=item_queue)
    json_data['message'] = "Success."
    json_data['data'] = data

    json_data = convert_datetime(json_data)
    return JSONResponse(json_data)

async def performer_level_receive_reward_level(request: Request):
    user, user_profile, error = await get_user_and_validate_session(request)
    if error:
        return error
    
    level_pk = int(request.path_params['level_pk'])

    user_performer_level_rewards = await get_user_performer_level_rewards(user["pk"])
    
    level_query = performerLevels.select().where(performerLevels.c.pk == level_pk)
    level = await manifest_database.fetch_one(level_query)

    user_performer_exp = await get_user_item(user['pk'], 'performerexp')
    user_performer_exp = user_performer_exp['amount'] if user_performer_exp else 0

    item_queue = {}
    granted = False

    exp_required = level['requiredPerformerEXP']
    if user_performer_exp >= exp_required:
        level_pk = level['pk']
        reward_exist = any(reward['PerformerLevelPk'] == level_pk for reward in user_performer_level_rewards)

        if not reward_exist:
            granted = True
            insert_query = userPerformerLevelRewards.insert().values(
                UserPk=user['pk'],
                PerformerLevelPk=level_pk,
                state=2,
                createdAt=datetime.utcnow(),
                updatedAt=datetime.utcnow()
            )
            pk = await player_database.execute(insert_query)
            
            reward = level['rewardItem']
            item_queue[reward['key']] = item_queue.get(reward['key'], 0) + reward['value']

    if granted:
        user_performer_level_reward = userPerformerLevelRewards.select().where((userPerformerLevelRewards.c.pk == pk))
        user_performer_level_reward = await player_database.fetch_one(user_performer_level_reward)
        user_performer_level_reward = dict(user_performer_level_reward)

    data = {
        "userPerformerLevelReward": user_performer_level_reward,
        "duplicatedItemKeys": [],
    }
    
    json_data, completed_ach = await get_standard_response(user, user_profile, item_list=item_queue)
    json_data['message'] = "Success."
    json_data['data'] = data

    json_data = convert_datetime(json_data)
    return JSONResponse(json_data)

async def performer_level_receive_reward_hurdle(request: Request):
    user, user_profile, error = await get_user_and_validate_session(request)
    if error:
        return error
    
    level_pk = int(request.path_params['level_pk'])
    user_performer_hurdle_missions = await get_user_performer_hurdle_missions(user["pk"])

    item_queue = {}
    cosmic_ticket = []

    for hurdle in user_performer_hurdle_missions:
        if hurdle['PerformerHurdleMissionPk'] == level_pk and hurdle['state'] == 1:
            update_query = userPerformerHurdleMissions.update().where(
                (userPerformerHurdleMissions.c.pk == hurdle['pk'])
            ).values(
                state=2
            )
            await player_database.execute(update_query)
            
            hurdle_mission_query = performerHurdleMissions.select().where(performerHurdleMissions.c.pk == hurdle['PerformerHurdleMissionPk'])
            hurdle_mission = await manifest_database.fetch_one(hurdle_mission_query)
            reward = hurdle_mission['rewardItem']
            item_queue[reward['key']] = item_queue.get(reward['key'], 0) + reward['value']
            if reward['key'].startswith('cosmicticket.'):
                cosmic_ticket.append(reward)

    data = {
        "cosmicTicketRewards": cosmic_ticket,
        "duplicatedItemKeys": [],
    }
    
    json_data, completed_ach = await get_standard_response(user, user_profile, item_list=item_queue)
    json_data['message'] = "Success."
    json_data['data'] = data

    json_data = convert_datetime(json_data)
    return JSONResponse(json_data)

route = [
    Route("/api/performerlevel/receive/reward/all", performer_level_receive_reward_all, methods=["POST"]),
    Route("/api/performerlevel/receive/reward/level/{level_pk}", performer_level_receive_reward_level, methods=["POST"]),
    Route("/api/performerlevel/receive/reward/hurdlemission/{level_pk}", performer_level_receive_reward_hurdle, methods=["POST"])
]