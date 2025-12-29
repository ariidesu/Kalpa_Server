from starlette.applications import Starlette
from starlette.responses import FileResponse, Response
from starlette.routing import Route
import os

# stupid loading sequence
from api.templates_norm import init_templates
from api.templates import init_templates_database
from api.play_session import load_play_session, start_cleanup_task
from api.cache import load_attendence_roster
init_templates()
load_play_session()

from api.database import player_database, manifest_database, init_db


from config import HOST, PORT, DEBUG, SSL_CERT, SSL_KEY, AUTH_MODE

if AUTH_MODE == 1:
    from api.email_hook import init_email
    init_email()

from api.user import route as user_routes
from api.auth import route as auth_routes
from api.base import route as base_routes
from api.darkmoon import route as darkmoon_routes
from api.lab import route as lab_routes
from api.noah import route as noah_routes
from api.play import route as play_routes
from api.performerlevel import route as performerlevel_routes
from api.usermission import route as userpermission_routes
from api.friend import route as friend_routes
from api.mailbox import route as mailbox_routes
from api.gacha import route as gacha_routes
from api.buy import route as buy_routes
from api.constellation import route as constellation_routes
from api.multiplay import route as multiplay_routes
from api.astralrating import route as astralrating_routes
from api.ranking import route as ranking_routes
from api.album import route as album_routes
from api.achievement import route as achievement_routes
from api.admin import route as admin_routes

root_folder = os.path.dirname(os.path.abspath(__file__))

allowed_folders = [
    "asset", "iconfiles", "eventbanner", "audfiles", "covfiles", "mapfiles", "web"
]

async def serve_file(request):
    path = request.path_params['path']
    first_level_folder = path.split('/')[0]
    if first_level_folder in allowed_folders:
        file_path = os.path.realpath(os.path.join(os.getcwd(), "files", path))
        if os.path.isfile(file_path):
            return FileResponse(file_path)

    return Response("File not found", status_code=404)

routes = []

routes = routes + user_routes + auth_routes + base_routes + darkmoon_routes + lab_routes + noah_routes + play_routes + performerlevel_routes + userpermission_routes + friend_routes + mailbox_routes + gacha_routes + buy_routes + constellation_routes + multiplay_routes + astralrating_routes + ranking_routes + album_routes + achievement_routes + admin_routes

if AUTH_MODE == 2:
    from api.discord_hook import routes as discord_routes
    routes = routes + discord_routes

routes.append(Route("/{path:path}", serve_file))

app = Starlette(debug=DEBUG, routes=routes)

@app.on_event("startup")
async def startup():
    await player_database.connect()
    await manifest_database.connect()
    await init_db()
    await init_templates_database()
    await start_cleanup_task()
    await load_attendence_roster()

@app.on_event("shutdown")
async def shutdown():
    await player_database.disconnect()
    await manifest_database.disconnect()

if __name__ == "__main__":
    import uvicorn
    ssl_context = (SSL_CERT, SSL_KEY) if SSL_CERT and SSL_KEY else None
    uvicorn.run(app, host=HOST, port=PORT, ssl_certfile=SSL_CERT, ssl_keyfile=SSL_KEY)

# Made By Tony  2025.8.30