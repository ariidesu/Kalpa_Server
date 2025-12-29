from starlette.responses import JSONResponse
from starlette.requests import Request
from starlette.routing import Route
from datetime import datetime, timezone
import json

from api.database import manifest_database, player_database, get_user_and_validate_session, userAlbums, albums, albumLampConditions, userAlbums, albumOpenConditions, userProfiles, check_mission, check_item_entitlement, performerHurdleMissions, userPerformerHurdleMissions, get_user_performer_hurdle_missions, userAlbumRecords, userAlbumBestRecords, get_user_achieved_list, ranking_cache, cache_database
from api.templates_norm import PLAY_PUBLIC_KEY, METADATA, ALBUM_SEASON
from api.misc import convert_datetime, get_standard_response, compress_string
from api.crypt import play_decrypt

async def check_performer_level_hurdle_missions(user_pk, stage_id):
    user_performer_hurdle_missions = await get_user_performer_hurdle_missions(user_pk)
    for hurdle in user_performer_hurdle_missions:
        if hurdle['state'] == 0:
            hurdle_pk = hurdle['PerformerHurdleMissionPk']
            hurdle_mission_query = performerHurdleMissions.select().where(performerHurdleMissions.c.pk == hurdle_pk)
            hurdle_mission = await manifest_database.fetch_one(hurdle_mission_query)
            if hurdle_mission:
                category = hurdle_mission['category']
                cleared = False
                if category == 19:
                    # clear specific stage
                    cleared = stage_id in hurdle_mission['targetPks']

                if cleared:
                    hurdle_progress = hurdle['current'] + 1
                    # Mark as cleared
                    query = userPerformerHurdleMissions.update().where((userPerformerHurdleMissions.c.UserPk == user_pk) & (userPerformerHurdleMissions.c.PerformerHurdleMissionPk == hurdle_pk)).values(
                        state = 1 if hurdle_progress >= hurdle_mission['goal'] else 0,
                        current = hurdle_progress if hurdle_progress <= hurdle_mission['goal'] else hurdle_mission['goal'],
                    )
                    await player_database.execute(query)


async def album_play_start(request: Request):
    user, user_profile, error = await get_user_and_validate_session(request)
    if error:
        return error
    
    request_post = await request.form()
    album_pk = int(request_post.get("AlbumPk", 0))

    data = {}
    item_queue = {}
    album_query = albums.select().where(albums.c.pk == album_pk)
    album = await manifest_database.fetch_one(album_query)
    album = dict(album) if album else None
    if not album:
        message = "Album not found."
        status = 400
    else:   
        item_queue[album['playMoneyKey']] = -album['minPrice']
        can_pay = await check_item_entitlement(user['pk'], item_queue)
        if not can_pay:
            message = "Not enough items to start album."
            status = 400
            item_queue = {}
        else:
            status = 200
            message = "Success."
            data['publicKey'] = PLAY_PUBLIC_KEY

    json_data, completed_ach = await get_standard_response(user, user_profile, item_list=item_queue)
    json_data['message'] = message
    json_data['data'] = data
    json_data = convert_datetime(json_data)
    return JSONResponse(json_data, status_code=status)

def check_lamp(lamp, play_data):
    end_state = play_data['endState']
    total_max_combo = play_data['totalMaxCombo']
    total_score = play_data['totalScore']
    avg_rate = play_data['avgRate']
    note_mode = play_data['noteMode']
    lunatic_mode = play_data['lunaticMode']
    hp = play_data['hp']
    stages = json.loads(play_data['stages'])
    speed = play_data['speed']

    lamp_criteria = lamp['conditionKey']
    lamp_value = lamp['conditionValue']

    if lamp_criteria == "clear_default":
        return True
    elif lamp_criteria == "clear_lunatic":
        return lunatic_mode == 1
    elif lamp_criteria == "gauge_over":
        return hp >= lamp_value
    elif lamp_criteria == "maxcombo_over":
        return total_max_combo >= lamp_value
    elif lamp_criteria == "score_over":
        return total_score >= lamp_value
    elif lamp_criteria == "miss_count" or lamp_criteria == "allcombo_all":
        if lamp_criteria == "allcombo_all":
            lamp_value = 0
        miss_count = 0
        for stage in stages:
            miss_count += stage['miss']
        return miss_count <= lamp_value
    elif lamp_criteria == "good_under_count":
        good_under_count = 0
        for stage in stages:
            good_under_count += stage['miss']
            good_under_count += stage['good']
        return good_under_count <= lamp_value
    elif lamp_criteria == "great_under_count" or lamp_criteria == "allperfect_all":
        if lamp_criteria == "allperfect_all":
            lamp_value = 0
        great_under_count = 0
        for stage in stages:
            great_under_count += stage['miss']
            great_under_count += stage['good']
            great_under_count += stage['great']
        return great_under_count <= lamp_value
    elif lamp_criteria == "perfect_count":
        perfect_count = 0
        for stage in stages:
            perfect_count += stage['perfect']
        return perfect_count >= lamp_value
    elif lamp_criteria == "speed_over":
        return speed >= lamp_value
    elif lamp_criteria == "rate_over":
        return avg_rate >= lamp_value
    elif lamp_criteria == "allcombo_one":
        has_all_combo = False
        for stage in stages:
            if stage['endState'] == 5:
                has_all_combo = True
        return has_all_combo
    elif lamp_criteria == "allperfect_one":
        has_all_perfect = False
        for stage in stages:
            if stage['endState'] == 6:
                has_all_perfect = True
        return has_all_perfect

async def album_play_end(request: Request):
    user, user_profile, error = await get_user_and_validate_session(request)
    if error:
        return error
    
    request_post = await request.form()
    play_data = await play_decrypt(request_post)
    album_pk = play_data['AlbumPk']
    end_state = play_data['endState']
    stages = json.loads(play_data['stages'])

    lamp_rewards = {}
    unlocked_album_list = []
    level_rewards = []

    album_query = albums.select().where(albums.c.pk == album_pk)
    album = await manifest_database.fetch_one(album_query)

    album_lamps_query = albumLampConditions.select().where(albumLampConditions.c.AlbumPk == album_pk).order_by(albumLampConditions.c.order.asc())
    album_lamps = await manifest_database.fetch_all(album_lamps_query)
    album_lamps = [dict(lamp) for lamp in album_lamps]

    user_album_query = userAlbums.select().where((userAlbums.c.UserPk == user['pk']) & (userAlbums.c.AlbumPk == album_pk))
    user_album = await player_database.fetch_one(user_album_query)
    user_album = dict(user_album)
    user_aqua_level = user_profile['thumbAquaLevel'] if album['finger'] == 0 else user_profile['multiAquaLevel']
    
    if not user_album:
        query = userAlbums.insert().values(
            avgRate=0,
            totalScore=0,
            progress=0,
            lamp1Status=0,
            lamp2Status=0,
            lamp3Status=0,
            createdAt=datetime.now(timezone.utc).isoformat(),
            updatedAt=datetime.now(timezone.utc).isoformat(),
            UserPk=user['pk'],
            AlbumPk=album_pk
        )
        await player_database.execute(query)
        query = userAlbums.select().where((userAlbums.c.UserPk == user['pk']) & (userAlbums.c.AlbumPk == album_pk))
        user_album = await player_database.fetch_one(query)
        user_album = dict(user_album)
    
    total_notes = 0
    for stage in stages:
        if stage['endState'] == 5:
            await check_mission(user['pk'], {"type": 5, "amount": 1})
        elif stage['endState'] == 6:
            await check_mission(user['pk'], {"type": 7, "amount": 1})
        await check_mission(user['pk'], {"type": 3, "amount": int(stage['TrackPk'])})
        total_notes += stage['perfect']
        total_notes += stage['great']
        total_notes += stage['good']

    await check_mission(user['pk'], {"type": 8, "amount": total_notes})

    if end_state < 3:
        # 0: NOT_CLEAR
        # 1: GIVE_UP
        # 2: RETRY
        # 3: CLEAR
        # 4: RISK_CLEAR
        # 5: FULLCOMBO_CLEAR
        # 6: PERFECT_CLEAR
        data = {"userAlbum": user_album}

    else:
        await check_mission(user['pk'], {"type": 1, "amount": 1})
        await check_mission(user['pk'], {"type": 6, "amount": 1})

        if play_data['noteMode'] == 1:
            await check_mission(user['pk'], {"type": 4, "amount": 1})
        lamp_1 = check_lamp(album_lamps[0], play_data)
        lamp_2 = check_lamp(album_lamps[1], play_data) if len(album_lamps) > 1 else False
        lamp_3 = check_lamp(album_lamps[2], play_data) if len(album_lamps) > 2 else False

        await check_performer_level_hurdle_missions(user['pk'], play_data['AlbumPk'])

        update_needed = False
        if lamp_1 and user_album['lamp1Status'] == 0:
            update_needed = True
            key = album['lampReward1']['key']
            value = album['lampReward1']['value']
            if key not in lamp_rewards:
                lamp_rewards[key] = value
            else:
                lamp_rewards[key] += value

            user_album['lamp1Status'] = 1
    
        if lamp_2 and user_album['lamp2Status'] == 0:
            update_needed = True
            key = album['lampReward2']['key']
            value = album['lampReward2']['value']
            if key not in lamp_rewards:
                lamp_rewards[key] = value
            else:
                lamp_rewards[key] += value

            user_album['lamp2Status'] = 1

        if lamp_3 and user_album['lamp3Status'] == 0:
            update_needed = True
            key = album['lampReward3']['key']
            value = album['lampReward3']['value']
            if key not in lamp_rewards:
                lamp_rewards[key] = value
            else:
                lamp_rewards[key] += value

            user_album['lamp3Status'] = 1
            
        if update_needed:
            query = userAlbums.update().where((userAlbums.c.UserPk == user['pk']) & (userAlbums.c.AlbumPk == album_pk)).values(
                lamp1Status=user_album['lamp1Status'],
                lamp2Status=user_album['lamp2Status'],
                lamp3Status=user_album['lamp3Status'],
                avgRate=play_data['avgRate'] if play_data['avgRate'] > user_album['avgRate'] else user_album['avgRate'],
                totalScore=play_data['totalScore'] if play_data['totalScore'] > user_album['totalScore'] else user_album['totalScore'],
                progress=1,
                updatedAt=datetime.now(timezone.utc)
            )
            await player_database.execute(query)

            if user_aqua_level < album['difficulty'] and album['type'] == 1:
                # user reached new aqua level, update profile
                user_aqua_level = album['difficulty']
                query = userProfiles.update().where(userProfiles.c.pk == user['pk']).values(
                    thumbAquaLevel=user_aqua_level if album['finger'] == 0 else user_profile['thumbAquaLevel'],
                    multiAquaLevel=user_aqua_level if album['finger'] == 1 else user_profile['multiAquaLevel'],
                    updatedAt=datetime.now(timezone.utc)
                )
                await player_database.execute(query)
                finger_query = 'THUMB' if album['finger'] == 0 else 'MULTI'
                level_rewards = METADATA['challengeAlbumReward'][finger_query][user_aqua_level - 1]

                for reward in level_rewards:
                    if reward['key'] not in lamp_rewards:
                        lamp_rewards[reward['key']] = reward['value']
                    else:
                        lamp_rewards[reward['key']] += reward['value']

            # get latest userAlbum
            query = userAlbums.select().where((userAlbums.c.UserPk == user['pk']) & (userAlbums.c.AlbumPk == album_pk))
            user_album = await player_database.fetch_one(query)
            user_album = dict(user_album)

            unlocked_albums_query = albumOpenConditions.select().where((albumOpenConditions.c.conditionKey == "clear_album") & (albumOpenConditions.c.conditionValue == album_pk))
            unlocked_albums = await manifest_database.fetch_all(unlocked_albums_query)
            unlocked_albums = [dict(a) for a in unlocked_albums]
            for albs in unlocked_albums:
                unlocked_album_list.append(albs['AlbumPk'])

        lamp_multiplier = 3 if user_album['lamp3Status'] == 1 else (2 if user_album['lamp2Status'] == 1 else (1 if user_album['lamp1Status'] == 1 else 0))

        data = {
            "userAlbum": user_album,
            "updatedLevel": user_aqua_level,
            "levelRewards": level_rewards,
            "unlockedUserAlbums": unlocked_album_list,
            "updatedLamp": [
                0,
                lamp_multiplier
            ]
        }
    
    query = userAlbumRecords.insert().values(
        season = ALBUM_SEASON,
        avgRate = play_data['avgRate'],
        totalScore = play_data['totalScore'],
        updatedAt = datetime.now(timezone.utc),
        createdAt = datetime.now(timezone.utc),
        AlbumPk = album_pk,
        UserPk = user['pk']
    )
    record_pk = await player_database.execute(query)

    existing_best_record_query = userAlbumBestRecords.select().where((userAlbumBestRecords.c.UserPk == user['pk']) & (userAlbumBestRecords.c.AlbumPk == album_pk) & (userAlbumBestRecords.c.season == ALBUM_SEASON))
    existing_best = await player_database.fetch_one(existing_best_record_query)

    if not existing_best or existing_best['avgRate'] < play_data['avgRate']:
        # nullify leaderboard cache
        cache_key = f"a_{album_pk}"
        cache_query = ranking_cache.delete().where(ranking_cache.c.key == cache_key)
        await cache_database.execute(cache_query)

        if not existing_best:
            # Insert new record
            query = userAlbumBestRecords.insert().values(
                season = ALBUM_SEASON,
                avgRate = play_data['avgRate'],
                totalScore = play_data['totalScore'],
                updatedAt = datetime.now(timezone.utc),
                createdAt = datetime.now(timezone.utc),
                AlbumPk = album_pk,
                UserPk = user['pk'],
                UserAlbumRecordPk = record_pk
            )

            await player_database.execute(query)
        else:
            # Update existing record
            query = userAlbumBestRecords.update().where(userAlbumBestRecords.c.pk == existing_best['pk']).values(
                state = ALBUM_SEASON,
                avgRate = play_data['avgRate'],
                totalScore = play_data['totalScore'],
                updatedAt = datetime.now(timezone.utc),
                UserAlbumRecordPk = record_pk
            )
            await player_database.execute(query)
    
    base_exp = play_data['avgRate'] / 10000 + lamp_multiplier * 20
    json_data, completed_ach = await get_standard_response(user, user_profile, item_list=lamp_rewards, performer_level_exp=base_exp)
    if len(completed_ach) > 0:
        data['achievedList'] = await get_user_achieved_list(user['pk'], completed_ach)
    
    json_data['data'] = await compress_string(data)
    json_data['message'] = "Success."
    json_data = convert_datetime(json_data)
    status = 200
    return JSONResponse(json_data, status_code=status)

route = [
    Route("/api/album/play/start", album_play_start, methods=["POST"]),
    Route("/api/album/play/end", album_play_end, methods=["POST"]),
]