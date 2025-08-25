import json
from pathlib import Path

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

class WebsocketManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

    async def broadcast_everyone_except_me(self, message: str, websocket: WebSocket):
        for connection in self.active_connections:
            if connection != websocket:
                await connection.send_text(message)

websocket_manager = WebsocketManager()
user_list = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    username = ''
    try:
        while True:
            json_massage = await websocket.receive_text()
            json_data = json.loads(json_massage)
            response_json = None
            if json_data.get('username'):
                username = json_data.get('username')
                user_list.append(username)
                response_json = {
                    "user_list" : user_list,
                }
                await websocket_manager.broadcast(json.dumps(response_json))
            if json_data.get('message'):
                message = f"{username}: {json_data.get('message')}"
                response_json = {
                    "message": message,
                }
                await websocket_manager.broadcast(json.dumps(response_json))
            if json_data.get('cursor'):
                data = str(json_data.get('cursor')).split(' ')
                cursor_name = data[0]
                x = int(data[1]) - 10
                y = int(data[2]) - 10
                html_div = f'<div style="width: 10px; height: 10px; background-color: black; position: absolute; top: {y}px; left: {x}px;"></div>'
                response_json = {
                        "cursor": html_div
                    }
                await websocket_manager.broadcast_everyone_except_me(json.dumps(response_json), websocket)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
        user_list.remove(username)
        response_json = {
            "user_list": user_list,
        }
        await websocket_manager.broadcast(json.dumps(response_json))

@app.get("/heartbeat")
def heart_bet():
    return Response()

# static_dir = Path(__file__).resolve().parent.parent / "frontend_vanila" / "static" / "chat_room"
static_dir = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")