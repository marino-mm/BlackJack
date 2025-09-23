import asyncio
from asyncio import Queue, Task, PriorityQueue, CancelledError
from functools import partial
from typing import Any, List, Set, Optional

from fastapi import FastAPI
from starlette.websockets import WebSocket, WebSocketDisconnect

from backend.model.BlackJack_game_models import Deck, Hand, Card, House, Player

BlackJack = FastAPI()


class BlackJackPlayer(Player):
    def __init__(self, ws: WebSocket):
        super().__init__()
        self.player_name = ''
        self.ws: WebSocket | Any = ws
        self.action_queue = Queue(10)
        self.ping_pong_queue = Queue(1)
        self.send_to_parent = False
        self.game = None
        self.worker_task: Task | Any = None
        self.ping_pong_task: Task | Any = None
        self.player_status: str = 'Connected'

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
        self.worker_task = asyncio.create_task(self.start_worker())
        self.ping_pong_task = asyncio.create_task(self.websocket_ping_pong())

    async def start_worker(self):
        try:
            while True:
                message_dict = await self.ws.receive_json()
                if message_dict.get("messageType") == "PingPong":
                    self.ping_pong_queue.put_nowait(message_dict)
                elif self.send_to_parent:
                    message_dict["player"] = self
                    if self.game:
                        self.game.game_queue.put_nowait(message_dict)
        except WebSocketDisconnect as e:
            print(f"Player {self.player_name} was disconnected")
            await self.disconnect_player()
        except Exception as e:
            print(
                f"Exception happened in player {self.player_name}, exception: {e}")

    async def websocket_ping_pong(self):
        try:
            while True:
                await asyncio.sleep(5)
                await self.ws.send_json({"PingPong": "Ping"})
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
            print(
                f"{self.player_name} was disconnected so websocket_ping_pong_task was cancelled.")

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
                print(f"Worker task and ping_pong_task were cancelled")
            except Exception as e:
                print(
                    f"Error happened in disconnect_player method. Error: {e}")

        self.player_status = "Disconnected"


class BlackJackGame:
    def __init__(self):
        self.all_players: List[BlackJackPlayer] = []
        self.sitting_players: List[Optional[BlackJackPlayer]] = [None for _ in range(5)]
        self.game_queue = PriorityQueue(100)
        self.house = House()
        self.deck = Deck()
        self.active_player: Optional[BlackJackPlayer] = None
        self.active_hand: Optional[Hand] = None
        self.active_hand_index: int = -1
        self.active_player_index: int = -1
        self.worker_task: Task | Any = None
        self.count_down_time = 30
        self.count_down_task: Task | Any = None
        self.running_tasks: Set[Task] = set()
        self.game_status = "waiting"

    async def player_move_worker(self):
        while True:
            message_dict = await self.game_queue.get()
            if self.game_status == "player_move_phase":
                if message_dict.get("new_slot_index") is not None:
                    self.move_slot(message_dict)
                    await self.send_data_to_all_players(self.send_slots())

    async def player_action_worker(self):
        while True:
            message_dict = await self.game_queue.get()
            if self.game_status == "player_action_phase":
                if message_dict.get("user", None) == self.active_player:
                    valid_move = await self.poccess_players_move(message_dict)
                    if valid_move:
                        await self.send_data_to_all_players(self.send_slots())
                        return True

    async def poccess_players_move(self, message_dict):
        if message_dict.get("messageType", '') == 'Action' and (action := message_dict.get("message", None)):
            if action == 'hit':
                self.active_hand.add_card(self.deck.get_card())
                if self.active_hand.is_busted:
                    pass

    async def game_round(self):
        while True:
            if self.game_status == 'waiting':
                pass

            if self.game_status == 'player_move_phase':
                await self.start_player_move_phase()
            

            self.game_status = 'player_action_phase'

            self.game_status = 'end_phase'
            if not self.count_down_task:
                self.count_down_task = asyncio.create_task(
                    self.count_down_worker())

    async def start_player_move_phase(self):
        for player in self.all_players:
            player.send_to_parent = True
        await self.send_round_title("Moving places and betting time")
        self.count_down_time = 30
        player_move_task = asyncio.create_task(self.player_move_worker())
        count_down_task = asyncio.create_task(self.count_down_worker())
        done, pending = await asyncio.wait([player_move_task, count_down_task], timeout=60, return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()
        for player in self.all_players:
            player.send_to_parent = False

    def move_slot(self, message):
        user: BlackJackPlayer = message.get("player")
        new_slot = message.get("new_slot_index")
        try:
            old_index = self.sitting_players.index(user)
        except ValueError:
            old_index = None
        target_slot = self.sitting_players[new_slot]
        if target_slot is None:
            self.sitting_players[new_slot] = user
            if old_index is not None:
                self.sitting_players[old_index] = None

    async def count_down_worker(self):
        while self.count_down_time > 0:
            await asyncio.sleep(1)
            self.count_down_time -= 1
            data = {"timeRemaining": self.count_down_time}
            await self.send_data_to_all_players(data)
        else:
            return "Countdown done"

    async def send_data_to_all_players(self, data):
        for player in self.all_players:
            await player.ws.send_json(data)

    async def start_count_down(self, time: int):
        self.count_down_time = time
        if not self.count_down_task:
            self.count_down_task = asyncio.create_task(
                self.count_down_worker(), name="count_down_task")
            self.running_tasks.add(self.count_down_task)

    async def stop_count_down(self):
        try:
            self.count_down_time = 0
            self.running_tasks.remove(self.count_down_task)
            self.count_down_task.cancel()
        except asyncio.CancelledError:
            pass

    async def add_player(self, player: BlackJackPlayer):
        self.all_players.append(player)
        if self.game_status != "waiting":
            await self.send_data_to_all_players(self.send_slots())
        else:
            self.game_status = "Running"
            self.worker_task = asyncio.create_task(
                self.queue_worker(), name="game_queue_worker")
            self.running_tasks.add(self.worker_task)
            await self.players_move_phase()

    async def remove_player(self, player: BlackJackPlayer):
        self.all_players.remove(player)
        if len(self.all_players) == 0:
            print("canceling countdown task")
            self.game_status = "waiting"
            for running_task in self.running_tasks:
                print(running_task.get_name())
                running_task.cancel()

    async def send_round_title(self, round_title: str):
        await self.send_data_to_all_players({"eventName": round_title})

    @staticmethod
    def frontend_dict(player: BlackJackPlayer) -> dict:
        return {"name": player.player_name, "hands": player.hands_json()}

    def send_slots(self):
        return {
            "slot_list": [self.frontend_dict(x) if x is not None else None for x in self.sitting_players],
        }

    async def players_action_phase(self):
        for player in self.sitting_players:
            self.active_player = player
            # type: ignore
            await self.send_data_to_all_players({"activ_player_username": self.active_player.player_name})
            active_hand_index = 0
            while active_hand_index < len(player.hands):  # type: ignore
                active_hand = player.hands[active_hand_index]  # type: ignore
                active_hand.is_active_hand = True
                await self.send_data_to_all_players(self.send_slots())


game = BlackJackGame()


@BlackJack.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    blackjack_player = None
    try:
        await ws.accept()
        blackjack_player = BlackJackPlayer(ws)
        await blackjack_player.player_creation(game)
        await game.add_player(blackjack_player)

        await blackjack_player.ping_pong_task
    except CancelledError:
        print(f"Cancelled Error in websocket_endpoint")
    except Exception as e:
        if blackjack_player:
            await blackjack_player.disconnect_player()
            print(f"Exception happened in websocket_endpoint, exception: {e}")
