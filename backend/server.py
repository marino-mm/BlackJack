import mimetypes
from pathlib import Path

from fastapi import FastAPI, Response, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# from backend.subapp.BlackJack_app import BlackJack
from backend.subapp.BlackJack_app2 import BlackJack

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIST = BASE_DIR / "backend"
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"
FRONTEND_VANILLA_DIST = BASE_DIR / "frontend_vanilla" / "static" / "chat_room"
# mimetypes are needed to be set because of Windows registry
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("image/svg+xml", ".svg")


@app.get("/heartbeat")
def heart_bet():
    return Response()


# app.mount("/game", game_app)
app.mount("/game", BlackJack)

# app.mount("/vanilla_js", StaticFiles(directory=FRONTEND_VANILLA_DIST, html=True, check_dir=True), name="vanilla_static")
# app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True, check_dir=True), name="static")


@app.get("/react/{full_path:path}")
async def serve_react_index(request: Request, full_path: str):
    file_path = FRONTEND_DIST / full_path
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)

    return FileResponse(FRONTEND_DIST / "index.html")


app.mount("/react", StaticFiles(directory=FRONTEND_DIST), name="static")
app.mount("/", StaticFiles(directory=FRONTEND_VANILLA_DIST,
          html=True, check_dir=True), name="static",)
