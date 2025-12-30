
from starlette.responses import JSONResponse
from starlette.requests import Request
from starlette.routing import Route
from datetime import datetime, timedelta

from api import database
from api.misc import check_email, generate_otp
from api.database import player_database, binds, users
from api.decorators import require_authorization, validate_form_fields, check_discord_api_key

@require_authorization(mode_required=[2])
@validate_form_fields(["discord_id"])
@check_discord_api_key()
async def discord_get_token(request: Request, form):
    email = form.get("email")
    discord_id = form.get("discord_id")

    existing_bind_query = binds.select().where((binds.c.bindAccount == discord_id) & (binds.c.isVerified == 1))
    existing_bind = await player_database.fetch_one(existing_bind_query)
    existing_bind = dict(existing_bind) if existing_bind else None

    token, hash = generate_otp()

    if existing_bind:
        # User is already verified
        existing_user_query = users.select().where(users.c.pk == existing_bind['UserPk'])
        existing_user = await player_database.fetch_one(existing_user_query)
        existing_user = dict(existing_user) if existing_user else None

        if not existing_user:
            return JSONResponse({"state": 0, "message": "User associated with this bind does not exist."}, status_code=405)
        
        if existing_user['permission'] < 0:
            return JSONResponse({"state": 0, "message": "This account is banned and cannot receive codes."}, status_code=400)
        
        if email and email != existing_user['email']:
            return JSONResponse({"state": 0, "message": "Email does not match the bound account."}, status_code=400)
        
        last_generate_date = existing_user['emailCodeExpireDate'] if existing_user['emailCodeExpireDate'] else None
        if last_generate_date:
            last_generate_date = datetime.fromisoformat(last_generate_date) - timedelta(minutes=10)
            if (datetime.utcnow() - last_generate_date).total_seconds() < 60:
                return JSONResponse({"state": 0, "message": "Too many requests. Please wait a while before retrying."}, status_code=400)
        
        expire_at_db = datetime.utcnow() + timedelta(minutes=10).isoformat()
        update_query = users.update().where(users.c.pk == existing_bind['UserPk']).values(
            emailCode=token,
            emailCodeExpireDate=expire_at_db
        )
        await player_database.execute(update_query)

        return JSONResponse({"state": 1, "message": "Your verification code is: " + token})
    
    else:
        if not email:
            return JSONResponse({"state": 0, "message": "Email is required for new binds."}, status_code=400)
        
        if not check_email(email):
            return JSONResponse({"state": 0, "message": "Invalid email."}, status_code=400)

        existing_user_query = users.select().where(users.c.email == email)
        user = await player_database.fetch_one(existing_user_query)
        user = dict(user) if user else None

        if user:
            existing_bind_query = binds.select().where(binds.c.UserPk == user['pk']).where(binds.c.isVerified == 1)
            existing_user_bind = await player_database.fetch_one(existing_bind_query)
            existing_user_bind = dict(existing_user_bind) if existing_user_bind else None
            if existing_user_bind:
                return JSONResponse({"state": 0, "message": "This email is already binded to someone else."}, status_code=400)
            
        else:
            return JSONResponse({"state": 0, "message": "No user associated with this email."}, status_code=400)

        # User is not verified yet
        existing_query = binds.select().where(binds.c.bindAccount == discord_id)
        existing_bind = await player_database.fetch_one(existing_query)
        existing_bind = dict(existing_bind) if existing_bind else None

        exipre_at_db = datetime.utcnow() + timedelta(minutes=10).isoformat()

        if existing_bind:
            # But a previously unverified bind exists
            last_generate_date = user['emailCodeExpireDate'] if user['emailCodeExpireDate'] else None
            if last_generate_date:
                last_generate_date = last_generate_date - timedelta(minutes=10)
                if (datetime.utcnow() - last_generate_date).total_seconds() < 60:
                    return JSONResponse({"state": 0, "message": "Too many requests. Please wait a while before retrying."}, status_code=400)
                
            update_query = users.update().where(users.c.pk == user["pk"]).values(emailCode=token, emailCodeExpireDate=exipre_at_db)
            await player_database.execute(update_query)

        else:
            # This is a fresh user
            insert_query = binds.insert().values(
                UserPk=user['pk'],
                bindAccount=discord_id,
                isVerified=0
            )
            await player_database.execute(insert_query)

            update_query = users.update().where(users.c.pk == user["pk"]).values(emailCode=token, emailCodeExpireDate=exipre_at_db)
            await player_database.execute(update_query)

    return JSONResponse({"state": 1, "message": "Your verification code: " + token})

@require_authorization(mode_required=[2])
@validate_form_fields(["discord_id"])
@check_discord_api_key()
async def discord_get_bind(request: Request, form):
    discord_id = form.get("discord_id")

    query = binds.select().where(binds.c.bindAccount == discord_id).where(binds.c.isVerified == 1)
    bind_record = await player_database.fetch_one(query)
    bind_record = dict(bind_record) if bind_record else None
    if not bind_record:
        return JSONResponse({"state": 0, "message": "No verified bind found for this Discord ID."}, status_code=404)
    
    user_query = users.select().where(users.c.pk == bind_record['UserPk'])
    user_record = await player_database.fetch_one(user_query)

    user_record = dict(user_record) if user_record else None
    if not user_record:
        return JSONResponse({"state": 0, "message": "User associated with this bind does not exist."}, status_code=405)
    
    username = user_record['id'] if user_record['id'] else "USERNAME NOT SET YET"
    
    return JSONResponse({"state": 1, "message": "Your account is binded to: " + username + ", email: " + user_record['email']})

@require_authorization(mode_required=[2])
@validate_form_fields(["discord_id"])
@check_discord_api_key()
async def discord_ban(request: Request, form):
    discord_id = form.get("discord_id")
    
    query = binds.select().where(binds.c.bindAccount == discord_id).where(binds.c.isVerified == 1)
    bind_record = await player_database.fetch_one(query)

    bind_record = dict(bind_record) if bind_record else None

    if not bind_record:
        return JSONResponse({"state": 0, "message": "No verified bind found for this Discord ID."}, status_code=404)
    
    existing_user_query = users.select().where(users.c.pk == bind_record['UserPk'])
    existing_user = await player_database.fetch_one(existing_user_query)

    if existing_user:
        if existing_user['permission'] <= 0:
            return JSONResponse({"state": 0, "message": "The account associated with this Discord ID is already banned."}, status_code=400)
    
        update_query = users.update().where(users.c.pk == bind_record['UserPk']).values(
            permission=-existing_user['permission']
        )
        await player_database.execute(update_query)

        return JSONResponse({"state": 1, "message": "The account associated with this Discord ID has been banned."})
    
    else:
        return JSONResponse({"state": 0, "message": "User associated with this bind does not exist."}, status_code=405)

@require_authorization(mode_required=[2])
@validate_form_fields(["discord_id"])
@check_discord_api_key()
async def discord_unban(request: Request, form):
    discord_id = form.get("discord_id")
    
    query = binds.select().where(binds.c.bindAccount == discord_id).where(binds.c.isVerified == 1)
    bind_record = await player_database.fetch_one(query)
    bind_record = dict(bind_record) if bind_record else None

    if not bind_record:
        return JSONResponse({"state": 0, "message": "No verified bind found for this Discord ID."}, status_code=404)

    existing_user_query = users.select().where(users.c.pk == bind_record['UserPk'])
    existing_user = await player_database.fetch_one(existing_user_query)
    existing_user = dict(existing_user) if existing_user else None

    if existing_user:
        if existing_user['permission'] > 0:
            return JSONResponse({"state": 0, "message": "The account associated with this Discord ID is not in an unbannable state."}, status_code=400)
    
        update_query = users.update().where(users.c.pk == bind_record['UserPk']).values(
            permission=-existing_user['permission']
        )
        await database.execute(update_query)
        return JSONResponse({"state": 1, "message": "The account associated with this Discord ID has been unbanned."})
    
    else:
        return JSONResponse({"state": 0, "message": "User associated with this bind does not exist."}, status_code=405)

routes = [
    Route('/discord/get_token', discord_get_token, methods=['POST']),
    Route('/discord/get_bind', discord_get_bind, methods=['POST']),
    Route('/discord/ban', discord_ban, methods=['POST']),
    Route('/discord/unban', discord_unban, methods=['POST'])
]