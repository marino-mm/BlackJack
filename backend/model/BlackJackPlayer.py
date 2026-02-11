from asyncio import CancelledError, Queue, Task, sleep, wait_for
import pprint
from typing import TYPE_CHECKING, Any, Optional

from fastapi import WebSocketDisconnect
from pydantic import TypeAdapter, ValidationError
from starlette.websockets import WebSocket

from backend.model.PlayerMessageJSON import IncomingMessage

if TYPE_CHECKING:
    from .BlackJackGame import BlackJackGame
    from .BlackJackGameState import GameState

from asyncio import create_task as ct

from backend.model.BlackJack_game_models import Player
from backend.model.PlayerMessage import PlayerMessage


class BlackJackPlayer(Player):
    def __init__(self, ws: WebSocket):
        super().__init__()
        self.player_name = ""
        self.ws: WebSocket | Any = ws
        self.ping_pong_queue = Queue(1)
        self.send_to_parent = False
        self.game: Optional["BlackJackGame"] = None
        self.outbound_queue = Queue()

        # self.receiver_task: Task = ct(self.receive_loop())
        # self.sender_task: Task = ct(self.send_loop())
        # self.ping_pong_task: Task = ct(self.websocket_ping_pong())

        self.receiver_task: Optional[Task] = None
        self.sender_task: Optional[Task] = None
        self.ping_pong_task: Optional[Task] = None

        self.player_status: str = "Connected"

    def __hash__(self):
        return hash(self.player_name)

    def __eq__(self, other):
        if isinstance(other, BlackJackPlayer):
            return self.player_name == other.player_name
        else:
            return False

    @classmethod
    async def player_creation_cls(cls, ws, game):
        self = cls(ws)
        while not self.player_name:
            message_dict = await self.ws.receive_json()
            if message_dict.get("username"):
                self.player_name = message_dict.get("username")

        self.game = game
        self.receiver_task = ct(self.receive_loop())
        self.sender_task = ct(self.send_loop())
        # self.ping_pong_task = ct(self.websocket_ping_pong())

        return self

    async def receive_loop(self):
        incoming_adapter = TypeAdapter(IncomingMessage)
        try:
            while True:
                message_dict = await self.ws.receive_json()
                try:
                    msg = incoming_adapter.validate_python(message_dict)
                except ValidationError as e:
                    # print(f"Error validating JSON message: {e}")
                    pprint.pp(incoming_adapter.json_schema())
                if message_dict.get("messageType") == "PingPong":
                    self.ping_pong_queue.put_nowait(message_dict)
                elif self.send_to_parent:
                    player_message = PlayerMessage(self, self.game, message_dict["messageType"], message_dict)
                    if self.game:
                        self.game.game_queue.put_nowait(player_message)
        except WebSocketDisconnect:
            print(f"Player {self.player_name} was disconnected")
            await self.disconnect_player()
        except Exception as e:
            print(f"Exception happened in player {self.player_name}, exception: {e}")
            await self.disconnect_player()

    def send(self, data: "GameState"):
        self.outbound_queue.put_nowait(data)
    
    async def send_loop(self):
        try:
            while True:
                data: GameState = await self.outbound_queue.get()
                await self.ws.send_text(data.model_dump_json(exclude_none=True))
        except WebSocketDisconnect:
            print(f"Player {self.player_name} was disconnected")
            await self.disconnect_player()
        except Exception as e:
            print(f"Exception happened in player {self.player_name}, exception: {e}")

    async def websocket_ping_pong(self):
        try:
            while True:
                await sleep(15)
                await self.ws.send_json({"PingPong": "Ping"})
                try:
                    await wait_for(self.ping_pong_queue.get(), timeout=5)
                except TimeoutError:
                    print(f"No Pong response from {self.ws}")
                    await self.ws.close(reason="Pong not received")
                    raise WebSocketDisconnect
        except WebSocketDisconnect:
            print(f"{self.player_name} disconnected due to missing Pong.")
            await self.disconnect_player()
        except CancelledError:
            print(f"{self.player_name} was disconnected so websocket_ping_pong_task was cancelled.")

    async def disconnect_player(self):
        if self.player_status == "Connected":
            try:
                if self.receiver_task:
                    self.receiver_task.cancel()
                if self.ping_pong_task:
                    self.ping_pong_task.cancel()
                if self.game:
                    # await self.game.remove_player(self)
                    message = PlayerMessage(self, self.game, "Disconnect")
                    await self.game.game_queue.put(message)
            except CancelledError:
                print("Worker task and ping_pong_task were cancelled")
            except Exception as e:
                print(f"Error happened in disconnect_player method. Error: {e}")

        self.player_status = "Disconnected"
