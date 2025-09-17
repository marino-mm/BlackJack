import json
import mimetypes
from pathlib import Path
from typing import Set

from fastapi import FastAPI, WebSocket, Response, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect

from backend.subapp.BlackJack_app import BlackJackGame, BlackJack
from subapp.main import game_app

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIST = BASE_DIR / "backend"
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"
FRONTEND_VANILLA_DIST = BASE_DIR / "frontend_vanilla" / "static" / "chat_room"
# mimetypes are needed to be set because of Windows registry
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("image/svg+xml", ".svg")


class UserConnection:
    def __init__(self, websocket: WebSocket):
        self.connection = websocket
        self.username = None

    async def create(self):
        while not self.username:
            message_dict = await self.connection.receive_json()
            if message_dict.get("username"):
                self.username = message_dict.get("username")

    def __eq__(self, value: object) -> bool:
        if isinstance(value, UserConnection):
            return self.username == value.username
        return False

    def __hash__(self):
        return hash(self.username)


class WebsocketManager:
    def __init__(self) -> None:
        self.active_connections: Set[UserConnection] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        user_connection = UserConnection(websocket)
        await user_connection.create()
        self.active_connections.add(user_connection)
        await self.broadcast_user_list()
        return user_connection

    async def disconnect(self, user_connection):
        self.active_connections.discard(user_connection)
        await self.broadcast_user_list()

    async def send_personal_message(
        self, message: str, user_connection: UserConnection
    ):
        await user_connection.connection.send_text(message)

    async def broadcast(self, message: str):
        try:
            for user_connection in self.active_connections:
                await user_connection.connection.send_text(message)
        except Exception:
            await self.disconnect(user_connection)

    async def broadcast_everyone_except_me(
        self, message: str, my_connection: UserConnection
    ):
        try:
            for user_connection in self.active_connections:
                if user_connection != my_connection:
                    await user_connection.connection.send_text(message)
        except Exception:
            await self.disconnect(user_connection)

    async def broadcast_user_list(self):
        user_list = []
        for user_connection in self.active_connections:
            user_list.append(user_connection.username)
        response_json = {"type": "user_list", "user_list": user_list}
        try:
            for user_connection in self.active_connections:
                await user_connection.connection.send_text(json.dumps(response_json))
        except Exception:
            await self.disconnect(user_connection)


websocket_manager = WebsocketManager()
user_list = []


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        user_connection = await websocket_manager.connect(websocket)
        while True:
            json_data = await user_connection.connection.receive_json()
            if json_data.get("message"):
                # message = f"{user_connection.username}: {json_data.get('message')}"
                response_json = {
                    "type": "message",
                    "user": user_connection.username,
                    "message": json_data.get("message"),
                }
                await websocket_manager.broadcast(json.dumps(response_json))
            if json_data.get("cursor"):
                response_json = {
                    "type": "cursor",
                    "cursor": json_data.get("cursor"),
                }
                await websocket_manager.broadcast_everyone_except_me(
                    json.dumps(response_json), user_connection
                )
    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket)


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
app.mount(
    "/",
    StaticFiles(directory=FRONTEND_VANILLA_DIST, html=True, check_dir=True),
    name="static",
)
