from fastapi import FastAPI, WebSocket, Response
from fastapi.staticfiles import StaticFiles
from pyexpat.errors import messages
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


websocket_manager = WebsocketManager()
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    username = await websocket.receive_text()
    await websocket_manager.broadcast(f"New connection established. Username: {username}")
    try:
        while True:
            message = await websocket.receive_text()
            await websocket_manager.broadcast(message)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
        await websocket_manager.broadcast(f"User {username} disconnected")

@app.get("/heartbeat")
async def heart_bet():
    return Response()



app.mount("/", StaticFiles(directory="static", html=True), name="static")
