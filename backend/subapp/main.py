from typing import Set

from fastapi import FastAPI
from starlette.websockets import WebSocket, WebSocketDisconnect

from backend.model.BlackJack_game_models import Deck

game_app = FastAPI()


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
        if isinstance(value, UserConnection):
            return self.username == value.username
        return False

    def __hash__(self):
        return hash(self.username)

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

    def remove_Listener(self, listener):
        self.listening_players.remove(listener)

    def send_data_to_user(self, listener):
        pass

    def send_data_to_all(self):
        for listener in self.listening_players:
            self.send_data_to_user(listener)

    async def start_game(self):
        print("Game started")
        self.STATUS = 'Playing'
        for player in self.listening_players:
            try:
                while True:
                    message = await player.connection.receive_json()
                    await player.connection.send_json(message)
                    print(self.listening_players)
            except Exception as e:
                print(f"Error u start_game-u{e}")




gameTable = GameTable()


@game_app.websocket('/ws')
async def game_loop(websocket: WebSocket):
    try:
        await websocket.accept()
        user = UserConnection(websocket)
        await user.create()
        gameTable.add_Listener(user)
        if gameTable.STATUS != 'Playing':
            await gameTable.start_game()
    except Exception as e:
        print(f"Error u game_loop-u{e}")
