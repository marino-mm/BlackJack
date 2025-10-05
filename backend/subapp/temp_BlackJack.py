
from asyncio import Queue, Task
from dataclasses import dataclass
from typing import List, Optional, Set

from backend.model.BlackJack_game_models import Deck, Hand, House
from backend.subapp.BlackJack_app import BlackJackPlayer


@dataclass
class PlayerMessage():

    player: BlackJackPlayer
    game: BlackJackGame
    type: str


class BlackJackGame:
    def __init__(self):
        self.all_players: List[BlackJackPlayer] = []
        self.sitting_players: List[Optional[BlackJackPlayer]] = [
            None for _ in range(5)]
        self.game_title = ""

        self.game_queue = Queue(100)

        self.house = House()
        self.deck = Deck()

        self.active_player: Optional[BlackJackPlayer] = None
        self.active_hand: Optional[Hand] = None
        self.active_hand_index: int = -1
        self.active_player_index: int = -1

        self.countdown_time = 30
        self.countdown_worker: Optional[Task] = None

        self.running_tasks: Set[Task] = set()

        self.game_status = "waiting"

    async def game_worker(self):
        while True:
            message: PlayerMessage = self.game_queue.get()

            if message.type == 'Join':
                await self.add_player(message.player)
            elif message.type == 'Disconect':
                await self.remove_player(message.player)

    async def add_player(self, player: BlackJackPlayer):
        self.all_players.append(player)
        # await self.send_slots()
        # await self.send_countdown_time()
        # await self.send_game_title()
        # await self.send_house_hand(full=False)

        if self.game_status == "waiting":
            self.game_status = "game_running"
            # game_running_task = ct(self._game_running(), name="game_1_task")
            # self.running_tasks.add(game_running_task)

    async def remove_player(self, player: BlackJackPlayer):
        self.all_players.remove(player)
        if len(self.all_players) == 0:
            self.shutdown_game()

    def shutdown_game(self):
        print("Game shut down")
        self.game_status = "waiting"
        for running_task in self.running_tasks:
            running_task.cancel()
