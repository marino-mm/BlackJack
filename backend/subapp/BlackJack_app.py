from asyncio import Queue, Task, PriorityQueue, CancelledError, sleep
from asyncio import create_task as ct
import asyncio

from typing import Any, List, Set, Optional

from fastapi import FastAPI
from starlette.websockets import WebSocket, WebSocketDisconnect

from backend.model.BlackJack_game_models import Deck, Hand, House, Player

BlackJack = FastAPI()


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
                    if self.game:
                        self.game.game_queue.put_nowait(message_dict)
        except WebSocketDisconnect:
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
                print(
                    f"Error happened in disconnect_player method. Error: {e}")

        self.player_status = "Disconnected"


class BlackJackGame:
    def __init__(self):
        self.all_players: List[BlackJackPlayer] = []
        self.sitting_players: List[Optional[BlackJackPlayer]] = [
            None for _ in range(5)]
        self.game_title = ""

        self.game_queue = PriorityQueue(100)

        self.house = House()
        self.deck = Deck()

        self.active_player: Optional[BlackJackPlayer] = None
        self.active_hand: Optional[Hand] = None
        self.active_hand_index: int = -1
        self.active_player_index: int = -1

        self.countdown_time = 30
        self.countdown_worker: Task | Any = None

        self.running_tasks: Set[Task] = set()

        self.game_status = "waiting"

    async def _game_running(self):
        while True:
            if self.game_status == "waiting":
                self.shutdown_game()
                return False

            self.game_status = "game_move_phase"
            await self.game_move_phase()

            self.game_status = "game_deal_phase"
            await self.game_deal_phase()

            self.game_status = "game_action_phase"
            await self.game_action_phase()

            self.game_status = "end_phase"
            await self.game_end_phase()

    async def game_move_phase(self):
        self.game_title = "Moving phase"
        await self.send_game_title()

        self.countdown_time = 5
        for player in self.all_players:
            player.send_to_parent = True
        countdown_task = ct(self.countdown_task(), name="countdown_task")
        game_moving_task = ct(self.player_move_task(), name="game_moving_task")
        self.running_tasks.add(countdown_task)
        self.running_tasks.add(game_moving_task)

        done, pending = await asyncio.wait([countdown_task, game_moving_task], return_when="FIRST_COMPLETED")
        for player in self.all_players:
            player.send_to_parent = True
        for temp in done:
            self.running_tasks.remove(temp)
        for temp in pending:
            temp.cancel()
            self.running_tasks.remove(temp)

    async def game_deal_phase(self):
        self.game_title = "Deal phase"
        await self.send_game_title()
        sitting_players_reduced = self.sitting_players.copy()
        sitting_players_reduced = [x for x in reversed(
            self.sitting_players) if x is not None]

        for _ in range(2):
            for player in sitting_players_reduced:
                if not player:
                    continue
                if len(player.hands) == 0:
                    player.hands.append(Hand())
                player.hands[0].add_card(self.deck.get_card())
                await self.send_slots()
                await asyncio.sleep(0.5)

            self.house.hands[0].add_card(self.deck.get_card())
            await self.send_house_hand(False)
            await asyncio.sleep(0.5)

        return

    async def game_end_phase(self):
        self.game_title = "Game end phase"
        await self.send_game_title()
        await self.send_house_hand(True)
        await asyncio.sleep(5)

        self.house.clear_hands()

        for player in self.sitting_players:
            if player:
                player.clear_hands()

        await self.send_slots()
        await self.send_house_hand(True)
        await asyncio.sleep(5)
        return

    async def game_action_phase(self):
        sitting_players_reduced = self.sitting_players.copy()
        sitting_players_reduced = [x for x in reversed(
            self.sitting_players) if x is not None]
        for activ_player in sitting_players_reduced:
            self.active_player = activ_player
            self.active_player.send_to_parent = True
            self.game_title = f"{activ_player.player_name}'s turn"
            await self.send_game_title()
            await self.send_active_player()

            self.active_hand_index = 0
            while self.active_hand_index < len(self.active_player.hands):
                self.active_hand = self.active_player.hands[self.active_hand_index]
                self.active_hand.is_active_hand = True
                await self.send_slots()

                self.countdown_time = 10
                countdown_task = ct(self.countdown_task(),
                                    name="countdown_task")
                game_player_action_task = ct(self.player_action_task(
                ), name=f"game_{self.active_player.player_name}_action_task",)

                self.running_tasks.add(countdown_task)
                self.running_tasks.add(game_player_action_task)

                done, pending = await asyncio.wait(
                    [countdown_task, game_player_action_task],
                    return_when="FIRST_COMPLETED",
                )
                for temp in done:
                    self.running_tasks.remove(temp)
                for temp in pending:
                    temp.cancel()
                    self.running_tasks.remove(temp)

                self.active_hand_index += 1

            self.active_player.send_to_parent = False
        self.active_player = None
        self.active_hand_index = -1
        self.countdown_time = 0
        await self.send_active_player()
        await self.send_slots()
        await self.send_countdown_time()

    async def player_move_task(self):
        while True:
            message_dict = await self.game_queue.get()
            if self.game_status == "game_move_phase":
                if message_dict.get("new_slot_index") is not None:
                    self.move_slot(message_dict)
                    await self.send_slots()

    async def player_action_task(self):
        while True:
            message_dict = await self.game_queue.get()
            if self.game_status == "game_action_phase":
                if message_dict.get("player", None) == self.active_player:
                    valid_move = await self.poccess_players_move(message_dict)
                    if valid_move:
                        await self.send_slots()
                        return True

    async def poccess_players_move(self, message_dict):
        if message_dict.get("messageType", "") == "Action" and (
            action := message_dict.get("message", None)
        ):
            if action == "hit":
                self.active_hand.add_card(self.deck.get_card())
                await self.send_slots()
                if self.active_hand.is_busted:
                    return True
            if action == "stand":
                return True
            if action == "double_down":
                self.active_player.dobule_down_hand(
                    self.active_hand, self.deck.get_card()
                )
                await self.send_slots()
                return True
            if action == "split":
                self.active_player.split_hand(
                    self.active_hand, self.deck.get_card()
                )
                await self.send_slots()

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

    async def countdown_task(self):
        while self.countdown_time > 0:
            await self.send_countdown_time()
            await sleep(1)
            self.countdown_time -= 1
        await self.send_countdown_time()

    async def send_data_to_all_players(self, data):
        for player in self.all_players:
            await player.ws.send_json(data)

    async def start_countdown(self, time: int):
        self.countdown_time = time
        if not self.countdown_worker:
            self.countdown_worker = ct(
                self.countdown_worker(), name="countdown_task")
            self.running_tasks.add(self.countdown_worker)

    async def add_player(self, player: BlackJackPlayer):
        self.all_players.append(player)
        await self.send_slots()
        await self.send_countdown_time()
        await self.send_game_title()
        await self.send_house_hand(full=False)

        if self.game_status == "waiting":
            self.game_status = "game_running"
            game_running_task = ct(self._game_running(), name="game_1_task")
            self.running_tasks.add(game_running_task)

    async def remove_player(self, player: BlackJackPlayer):
        self.all_players.remove(player)
        if len(self.all_players) == 0:
            self.shutdown_game()

    async def send_game_title(self):
        await self.send_data_to_all_players({"eventName": self.game_title})

    async def send_active_player(self):
        if self.active_player:
            await self.send_data_to_all_players(
                {"activ_player_username": self.active_player.player_name}
            )

    async def send_slots(self):
        await self.send_data_to_all_players(
            {
                "slot_list": [
                    self.frontend_dict(x) if x is not None else None
                    for x in self.sitting_players
                ]
            }
        )

    async def send_house_hand(self, full=False):
        if len(self.house.hands[0].cards) > 0:
            if full:
                await self.send_data_to_all_players(
                    {"houseHand": self.house.hands_json()}
                )
            else:
                await self.send_data_to_all_players(
                    {"houseHand": self.house.partial_hand_json()}
                )

    async def send_countdown_time(self):
        await self.send_data_to_all_players({"timeRemaining": self.countdown_time})

    def shutdown_game(self):
        print("Game shut down")
        self.game_status = "waiting"
        for running_task in self.running_tasks:
            running_task.cancel()

    @staticmethod
    def frontend_dict(player: BlackJackPlayer) -> dict:
        return {"name": player.player_name, "hands": player.hands_json()}


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
        print("Cancelled Error in websocket_endpoint")
    except Exception as e:
        if blackjack_player:
            await blackjack_player.disconnect_player()
            print(f"Exception happened in websocket_endpoint, exception: {e}")
