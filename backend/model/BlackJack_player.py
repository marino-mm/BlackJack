from asyncio import CancelledError, Queue, Task
import asyncio
from typing import Any
from fastapi import WebSocketDisconnect
from starlette.websockets import WebSocket
from backend.model.BlackJack_game_models import Player
from asyncio import create_task as ct

from backend.model.PlayerMessage import PlayerMessage


class BlackJackPlayer(Player):
    def __init__(self, ws: WebSocket):
        super().__init__()
        self.player_name = ""
        self.ws: WebSocket | Any = ws
        self.action_queue = Queue(10)
        self.ping_pong_queue = Queue(1)
        self.send_to_parent = False
        self.game = None
        self.worker_task: Task | Any = None
        self.ping_pong_task: Task | Any = None
        self.player_status: str = "Connected"

    def __hash__(self):
        return hash(self.player_name)

    def __eq__(self, other):
        if isinstance(other, BlackJackPlayer):
            return self.player_name == other.player_name
        else:
            return False

    async def player_creation(self, game):
        while not self.player_name:
            message_dict = await self.ws.receive_json()
            if message_dict.get("username"):
                self.player_name = message_dict.get("username")

        self.game = game
        self.worker_task = ct(self.start_worker())
        self.ping_pong_task = ct(self.websocket_ping_pong())

    async def start_worker(self):
        try:
            while True:
                message_dict = await self.ws.receive_json()
                if message_dict.get("messageType") == "PingPong":
                    self.ping_pong_queue.put_nowait(message_dict)
                elif self.send_to_parent:
                    message_dict["player"] = self
                    player_message = PlayerMessage(
                        self, self.game, message_dict["type"], message_dict
                    )
                    if self.game:
                        self.game.game_queue.put_nowait(player_message)
        except WebSocketDisconnect:
            print(f"Player {self.player_name} was disconnected")
            await self.disconnect_player()
        except Exception as e:
            print(f"Exception happened in player {self.player_name}, exception: {e}")

    async def websocket_ping_pong(self):
        try:
            while True:
                await asyncio.sleep(5)
                await self.ws.send_json({"PingPong": "Ping"})
                try:
                    await asyncio.wait_for(self.ping_pong_queue.get(), timeout=5)
                except asyncio.TimeoutError:
                    print(f"No Pong response from {self.ws}")
                    await self.ws.close(reason="Pong not received")
                    raise WebSocketDisconnect
        except WebSocketDisconnect:
            print(f"{self.player_name} disconnected due to missing Pong.")
            await self.disconnect_player()
        except CancelledError:
            print(
                f"{self.player_name} was disconnected so websocket_ping_pong_task was cancelled."
            )

    async def disconnect_player(self):
        if self.player_status == "Connected":
            try:
                if self.worker_task:
                    self.worker_task.cancel()
                if self.ping_pong_task:
                    self.ping_pong_task.cancel()
                if self.game:
                    await self.game.remove_player(self)
            except CancelledError:
                print("Worker task and ping_pong_task were cancelled")
            except Exception as e:
                print(f"Error happened in disconnect_player method. Error: {e}")

        self.player_status = "Disconnected"
