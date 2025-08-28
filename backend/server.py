import json
import mimetypes
from pathlib import Path
from typing import Set

from fastapi import FastAPI, WebSocket, Response
from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIST = BASE_DIR / "backend"
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"
FRONTEND_VANILLA_DIST = BASE_DIR / "frontend_vanila" /"static"/ "chat_room"
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
            if message_dict.get('username'):
                self.username = message_dict.get('username').replace(' ', '_')

    def __eq__(self, value: object) -> bool:
        return self.username == value.username

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

    async def send_personal_message(self, message: str, user_connection: UserConnection):
        await user_connection.connection.send_text(message)

    async def broadcast(self, message: str):
        try:
            for user_connection in self.active_connections:
                await user_connection.connection.send_text(message)
        except Exception:
            await self.disconnect(user_connection)

    async def broadcast_everyone_except_me(self, message: str, my_connection: UserConnection):
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
        response_json = {"user_list": user_list}
        try:
            for user_connection in self.active_connections:
                await user_connection.connection.send_text(json.dumps(response_json))
        except Exception:
            await self.disconnect(user_connection)


websocket_manager = WebsocketManager()
user_list = []


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    user_connection = await websocket_manager.connect(websocket)
    try:
        response_json = None
        # user_list.append(user_connection.username)
        # response_json = {"user_list": user_list}
        # await websocket_manager.broadcast(json.dumps(response_json))
        while True:
            json_data = await user_connection.connection.receive_json()
            if json_data.get('message'):
                message = f"{user_connection.username}: {json_data.get('message')}"
                response_json = {
                    "message": message,
                }
                await websocket_manager.broadcast(json.dumps(response_json))
            if json_data.get('cursor'):
                response_json = {
                    "cursor": json_data.get('cursor'),
                }
                await websocket_manager.broadcast_everyone_except_me(json.dumps(response_json), user_connection)
    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket)


@app.get("/heartbeat")
def heart_bet():
    return Response()

# app.mount("/vanilla_js", StaticFiles(directory=FRONTEND_VANILLA_DIST, html=True, check_dir=True), name="vanilla_static")
# app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True, check_dir=True), name="static")
app.mount("/", StaticFiles(directory=FRONTEND_VANILLA_DIST, html=True, check_dir=True), name="static")

