import json

from fastapi import FastAPI, WebSocket, Response
from fastapi.staticfiles import StaticFiles
from pyexpat.errors import messages
from starlette.responses import FileResponse, RedirectResponse
from starlette.websockets import WebSocketDisconnect

app = FastAPI()

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


app.mount("/static", StaticFiles(directory="static", html=True), name="static")

@app.get("/")
def serve_index():
    return RedirectResponse("/chat", status_code=301)

@app.get("/chat")
def serve_chat():
    return FileResponse("static/chat_room/chat_room.html")

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
            if json_data.get('username'):
                username = json_data.get('username')
                user_list.append(username)
                response_json = {
                    "user_list" : user_list,
                }
            if json_data.get('message'):
                message = f"{username}: {json_data.get('message')}"
                response_json = {
                    "message": message,
                }
            await websocket_manager.broadcast(json.dumps(response_json))
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

