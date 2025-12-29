from starlette.responses import JSONResponse
from starlette.requests import Request
from starlette.routing import Route

from api.database import player_database, userMailboxes, get_user_and_validate_session, get_user_mailboxes, get_mail
from api.misc import get_standard_response, convert_datetime

async def mailbox_view(request: Request):
    user, user_profile, error = await get_user_and_validate_session(request)
    if error:
        return error
    
    mail_pk = int(request.path_params["mail_pk"])
    mail = await get_mail(mail_pk, user['pk'])

    if not mail:
        message = "Mail not found"
        status = 400
        data = {}

    else:
        upgrade_state = 1

        if len(mail['itemRewards']) == 0 and len(mail['packRewards']) == 0:
            upgrade_state = 2

        update_query = userMailboxes.update().where(
            (userMailboxes.c.pk == mail_pk) & (userMailboxes.c.UserPk == user['pk'])
        ).values(
            state=upgrade_state
        )
        await player_database.execute(update_query)
        message = "Success."
        status = 200
        data = {
            "userMailBox": mail
        }

    json_data, completed_ach = await get_standard_response(user, user_profile)
    json_data['message'] = message
    json_data['data'] = data

    json_data = convert_datetime(json_data)
    return JSONResponse(json_data, status_code=status)

async def mailbox_receive_reward(request: Request):
    user, user_profile, error = await get_user_and_validate_session(request)
    if error:
        return error
    
    mail_pk = int(request.path_params["mail_pk"])
    mail = await get_mail(mail_pk, user['pk'])

    if not mail:
        return JSONResponse({"message": "Mail not found"}, status_code=404)

    if mail['state'] == 2:
        return JSONResponse({"message": "Mail reward already claimed"}, status_code=400)
    
    item_queue = {}
    for reward in mail['itemRewards']:
        item_queue[reward['key']] = item_queue.get(reward['key'], 0) + reward['value']

    update_query = userMailboxes.update().where(
        (userMailboxes.c.pk == mail_pk) & (userMailboxes.c.UserPk == user['pk'])
    ).values(
        state=2
    )
    await player_database.execute(update_query)

    json_data, completed_ach = await get_standard_response(user, user_profile, item_list=item_queue)
    json_data['message'] = "Success."
    json_data['data'] = {
        "userMailBox": {
            **mail,
            "state": 2
        },
        "duplicatedItemKeys": [],
    }
    json_data = convert_datetime(json_data)
    return JSONResponse(json_data)

async def mailbox_all_delete(request: Request):
    user, user_profile, error = await get_user_and_validate_session(request)
    if error:
        return error
    
    mailboxes = await get_user_mailboxes(user['pk'])
    deletable_mail_pks = [mail['pk'] for mail in mailboxes if mail['state'] == 2]

    delete_query = userMailboxes.delete().where(
        (userMailboxes.c.pk.in_(deletable_mail_pks)) & (userMailboxes.c.UserPk == user['pk'])
    )
    await player_database.execute(delete_query)

    json_data, completed_ach = await get_standard_response(user, user_profile)
    json_data['message'] = "Success."
    json_data['data'] = {}
    json_data = convert_datetime(json_data)
    return JSONResponse(json_data)

route = [
    Route("/api/mailbox/{mail_pk}/view", mailbox_view, methods=["POST"]),
    Route("/api/mailbox/{mail_pk}/receive/reward", mailbox_receive_reward, methods=["POST"]),
    Route("/api/mailbox/all/delete", mailbox_all_delete, methods=["POST"])
]