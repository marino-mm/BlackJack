import asyncio
from asyncio import Queue
from os import remove
from typing import Set

from fastapi import FastAPI
from starlette.applications import Starlette
from starlette.websockets import WebSocket, WebSocketDisconnect

from backend.model.BlackJack_game_models import Deck

game_app = FastAPI()


class UserConnection:
    def __init__(self, websocket: WebSocket):
        self.connection = websocket
        self.username = None
        self.message_Queue = Queue(1)
        self.user_Status = None

    async def create(self):
        while not self.username:
            message_dict = await self.connection.receive_json()
            if message_dict.get('username'):
                self.username = message_dict.get('username')

        self.user_Status = 'Connected'

    async def start_listening(self):
        try:
            while True:
                message = await self.connection.receive_json()
                await self.message_Queue.put(message)
        except WebSocketDisconnect:
            print('Websocket disconnected')
            self.user_Status = 'Disconnected'
        except asyncio.CancelledError:
            print('Listening task cancelled')
            self.user_Status = 'Disconnected'
            raise

    def __eq__(self, value: object) -> bool:
        if isinstance(value, UserConnection):
            return self.username == value.username
        return False

    def __hash__(self):
        return hash((self.username, self.connection))

    def __str__(self):
        return self.username

    def __repr__(self):
        return str(self)


class GameTable:
    def __init__(self):
        self.listening_players = []
        self.STATUS = ''

    def add_Listener(self, listener):
        print("dodan frajer")
        # self.listening_players.add(listener)
        self.listening_players.append(listener)


    def remove_listener(self, listener):
        self.listening_players.remove(listener)

    async def send_json_to_user(self, listener, data):
        await listener.connection.send_json(data)

    async def send_json_to_all(self, data):
        for index, listener in enumerate(self.listening_players):
            try:
                print(listener.connection)
                await self.send_json_to_user(listener, data)
            except Exception as e:
                print(e)
                # print(index)
                pass
                # self.remove_listener(listener)

    async def start_game(self):
        print("Game started")
        self.STATUS = 'Playing'
        # for player in self.listening_players:
        player:UserConnection = self.listening_players[0]
        try:
            while True:
                if player.user_Status != 'Connected':
                    raise WebSocketDisconnect
                message = await player.message_Queue.get()
                await self.send_json_to_all(message)
        except Exception as e:
            self.remove_listener(player)
            self.STATUS = ''
            print(f"Error u start_game-u{e}")

async def websocketPingPong(ws: UserConnection):
    await asyncio.sleep(5)
    try:
        await ws.connection.send_json({"action": "Ping"})

        # Wait for Pong from message queue
        try:
            message = await asyncio.wait_for(ws.message_Queue.get(), timeout=5)
        except asyncio.TimeoutError:
            print(f"No Pong response from {ws.username}")
            await ws.connection.close(reason='Pong not received')
            raise WebSocketDisconnect

        if message.get('action', '') != 'Pong':
            print(f"Invalid Pong response from {ws.username}: {message}")
            await ws.connection.close(reason='Invalid Pong response')
            raise WebSocketDisconnect

    except WebSocketDisconnect:
        print(f"{ws.username} disconnected due to missing/invalid Pong.")
        gameTable.remove_listener(ws)



gameTable = GameTable()


@game_app.websocket('/ws')
async def game_loop(websocket: WebSocket):
    try:
        await websocket.accept()
        user = UserConnection(websocket)
        await user.create()
        gameTable.add_Listener(user)
        asyncio.create_task(user.start_listening())
        if gameTable.STATUS != 'Playing':
            asyncio.create_task(gameTable.start_game())
        while True:
            await websocketPingPong(user)

    except Exception as e:
        print(f"Error u game_loop-u{e}")
