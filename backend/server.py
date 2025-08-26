import json
from pathlib import Path
from tkinter import N
from typing import Dict, Set

from fastapi import FastAPI, WebSocket, Response
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketDisconnect

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserConnection:
    def __init__(self, websocket: WebSocket):
        self.connection = websocket
        self.username = None
        
    async def create(self):
        while not self.username:
            message_dict = await self.connection.receive_json()
            if message_dict.get('username'):
                self.username = message_dict.get('username')
    
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
        return user_connection

    def disconnect(self, user_connection):
        self.active_connections.discard(user_connection)

    async def send_personal_message(self, message: str, user_connection: UserConnection):
        await user_connection.connection.send_text(message)

    async def broadcast(self, message: str):
        for user_connection in self.active_connections:
            await user_connection.connection.send_text(message)

    async def broadcast_everyone_except_me(self, message: str, my_connection: UserConnection):
        for user_connection in self.active_connections:
            if user_connection != my_connection:
                await user_connection.connection.send_text(message)

websocket_manager = WebsocketManager()
user_list = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    user_connection = await websocket_manager.connect(websocket)
    try:
        response_json = None
        user_list.append(user_connection.username)
        response_json = {"user_list" : user_list}
        await websocket_manager.broadcast(json.dumps(response_json))
        while True:
            json_data = await user_connection.connection.receive_json()
            if json_data.get('message'):
                message = f"{user_connection.username}: {json_data.get('message')}"
                response_json = {
                    "message": message,
                }
                await websocket_manager.broadcast(json.dumps(response_json))
            if json_data.get('cursor'):
                data = str(json_data.get('cursor')).split(' ')
                cursor_name = data[0]
                x = int(data[1])
                y = int(data[2])
                html_div = f'<div id="{cursor_name}"style="width: 10px; height: 10px; background-color: blue; position: absolute; top: {y}px; left: {x}px;">cursor_name</div>'
                response_json = {
                        "cursor": html_div,
                        "cursor_username": cursor_name
                    }
                await websocket_manager.broadcast_everyone_except_me(json.dumps(response_json), user_connection)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
        user_list.remove(user_connection.username)
        response_json = {"user_list": user_list}
        await websocket_manager.broadcast(json.dumps(response_json))

@app.get("/heartbeat")
def heart_bet():
    return Response()

static_dir = Path(__file__).resolve().parent.parent / "frontend_vanila" / "static" / "chat_room"
# static_dir = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")