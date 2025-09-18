import asyncio
from asyncio import Queue, Task, PriorityQueue, CancelledError
from typing import Any, List

from fastapi import FastAPI
from starlette.websockets import WebSocket, WebSocketDisconnect

from ..model.BlackJack_game_models import Hand, Card, House

BlackJack = FastAPI()

class BlackJackPlayer:
    def __init__(self, ws: WebSocket):
        self.player_name = ''
        self.ws: WebSocket | Any = ws
        self.action_queue = Queue(10)
        self.ping_pong_queue = Queue(1)
        self.send_to_parent = False
        self.game = None
        self.worker_task: Task | Any = None
        self.ping_pong_task: Task | Any = None
        self.hands: List[Hand] | List[List[Card]] = []

    async def player_creation(self, game):
        while not self.player_name:
            message_dict = await self.ws.receive_json()
            if message_dict.get("username"):
                self.player_name = message_dict.get("username")

        self.game = game
        self.worker_task = asyncio.create_task(self.start_worker())
        self.ping_pong_task = asyncio.create_task(self.websocket_ping_pong())

    async def start_worker(self):
        try:
            while True:
                message_dict = await self.ws.receive_json()
                if message_dict.get("messageType") == "PingPong":
                    self.ping_pong_queue.put_nowait(message_dict)
                elif self.send_to_parent:
                    self.game.game_queue.put_nowait(message_dict)
        except WebSocketDisconnect as e:
            print(f"Player {self.player_name} was disconnected")
            await self.disconnect_player()
        except Exception as e:
            print(f"Exception happened in player {self.player_name}, exception: {e}")

    async def websocket_ping_pong(self):
        try:
            while True:
                await asyncio.sleep(5)
                await self.ws.send_json({"messageType": "PingPong", "message": "Ping"})
                try:
                    message = await asyncio.wait_for(self.ping_pong_queue.get(), timeout=5)
                except asyncio.TimeoutError:
                    print(f"No Pong response from {self.ws}")
                    await self.ws.close(reason="Pong not received")
                    raise WebSocketDisconnect
        except WebSocketDisconnect:
            print(f"{self.player_name} disconnected due to missing Pong.")
            await self.disconnect_player()
        except CancelledError:
            print(f"{self.player_name} was disconnected so websocket_ping_pong_task was cancelled.")

    async def disconnect_player(self):
        self.worker_task.cancel()
        self.ping_pong_task.cancel()
        await self.game.remove_player(self)

class BlackJackGame:
    def __init__(self):
        self.all_players:List[BlackJackPlayer] = []
        self.sitting_players: List[BlackJackPlayer] = []
        self.game_queue = PriorityQueue(100)
        self.House = House()
        self.worker_task: Task | Any = None
        self.count_down_time = 30
        self.count_down_task: Task | Any = None

    async def queue_worker(self):
        while True:
            message_dict = await self.game_queue.get()
            print(message_dict)

    async def count_down_worker(self):
        print("Counting down started")
        while self.count_down_time > 0:
            print(self.count_down_time)
            await asyncio.sleep(1)
            self.count_down_time -= 1
            for player in self.all_players:
                data = {
                    "messageType": "UpdateCountdownTime",
                    "timeRemaining": self.count_down_time,
                }
                await player.ws.send_json(data)
        else:
            self.count_down_time = 30
            return

    async def add_player(self, player: BlackJackPlayer):
        self.all_players.append(player)
        self.count_down_task = asyncio.create_task(self.count_down_worker())

    async def remove_player(self, player: BlackJackPlayer):
        self.all_players.remove(player)
        if len(self.all_players) == 0:
            print("canceling countdown task")
            self.count_down_task.cancel()



game = BlackJackGame()

@BlackJack.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    try:
        await ws.accept()
        blackjack_player = BlackJackPlayer(ws)
        await blackjack_player.player_creation(game)
        await game.add_player(blackjack_player)
        
        await blackjack_player.ping_pong_task
    except Exception as e:
        await blackjack_player.disconnect_player()
        print(f"Exception happened in websocket_endpoint, exception: {e}")