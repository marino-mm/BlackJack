from asyncio import Event, Queue, Task
from typing import List, Optional, Set

from backend.model.BlackJack_game_models import Deck, Hand, House
from backend.subapp.BlackJack_app import BlackJackPlayer


class BlackJackGame:
    def __init__(self):
        self.all_players: List[BlackJackPlayer] = []
        self.sitting_players: List[Optional[BlackJackPlayer]] = [None for _ in range(5)]
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

        self._next_hand = Event()

        self.game_status = "waiting"

    async def game_worker(self):
        while True:
            message = await self.game_queue.get()
            if message.type == "Join":
                await self.add_player(message.player)
            elif message.type == "Disconect":
                await self.remove_player(message.player)
            elif message.type == "MoveSlots":
                if message.data.get("new_slot_index") is not None:
                    self.move_slot(message.data)
                    # await self.send_slots()
            elif message.type == "PlayerAction":
                if message.player == self.active_player:
                    await self.poccess_players_move(message.data)

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

    async def poccess_players_move(self, message_dict):
        if message_dict.get("messageType", "") == "Action" and (action := message_dict.get("message", None)):
            if action == "hit":
                self.active_hand.add_card(self.deck.get_card())
                # await self.send_slots()
                if self.active_hand.is_busted:
                    self._next_hand.set()
            if action == "stand":
                self._next_hand.set()
            if action == "double_down":
                self.active_player.dobule_down_hand(self.active_hand, self.deck.get_card())
                # await self.send_slots()
                self._next_hand.set()
            if action == "split":
                self.active_player.split_hand(self.active_hand, self.deck.get_card())
                # await self.send_slots()

    def shutdown_game(self):
        print("Game shut down")
        self.game_status = "waiting"
        for running_task in self.running_tasks:
            running_task.cancel()
