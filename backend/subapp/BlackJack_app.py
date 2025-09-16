import asyncio
from asyncio import Queue, Task, PriorityQueue
from multiprocessing.pool import worker
from typing import Any, List

from fastapi import FastAPI
from starlette.websockets import WebSocket

from backend.model.BlackJack_game_models import Hand, Card, House

BlackJack = FastAPI()


class BlackJackPlayer:
    def __init__(self, ws: WebSocket):
        self.player_name = ''
        self.ws: WebSocket | Any = ws
        self.action_queue = Queue(10)
        self.ping_pong_queue = Queue(1)
        self.send_to_parent = False
        self.game = None
        self.worker: Task | Any = None
        self.hands: List[Hand] | List[List[Card]] = []

    async def player_creation(self, game):
        while not self.player_name:
            message_dict = await self.ws.receive_json()
            if message_dict.get("username"):
                self.player_name = message_dict.get("username")

        self.game = game
        self.worker = asyncio.create_task(worker())

    async def worker(self):
        try:
            while True:
                message_dict = await self.ws.receive_json()
                if message_dict.get("messageType") == "PingPong":
                    self.ping_pong_queue.put_nowait(message_dict)
                elif self.send_to_parent:
                    self.game.game_queue.no_wait(message_dict)
        except Exception as e:
            print(f"Exception happened in player {self.player_name}, exception: {e}")

    async def disconnect_player(self):
        self.worker.cancel()

class BlackJackGame:
    def __init__(self):
        self.all_players:List[BlackJackPlayer] = []
        self.sitting_players: List[BlackJackPlayer] = []
        self.game_queue = PriorityQueue(100)
        self.House = House()