from asyncio import Event, Queue, Task
from typing import List, Optional, Set
from backend.model.BlackJack_game_models import Deck, Hand, House
from backend.model.BlackJackPlayer import BlackJackPlayer, GameState
from backend.model.PlayerMessage import PlayerMessageTypeEnum
from asyncio import create_task as ct


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

        self.game_worker_task: Task = ct(self.game_worker(), name="game_worker_task")
        self.game_phase_task: Task = ct(self.game_worker(), name="game_worker_task")
        self.running_tasks: Set[Task] = set()
        self.running_tasks.add(self.game_worker_task)
        
        self._next_hand = Event()
        self._game_running = Event()
        self.game_status = "waiting"

    async def game_worker(self):
        while True:
            message = await self.game_queue.get()
            if message.type == PlayerMessageTypeEnum.JOIN:
                await self.add_player(message.player)
            elif message.type == PlayerMessageTypeEnum.DISCONNECT:
                await self.remove_player(message.player)
            elif message.type == PlayerMessageTypeEnum.MOVE:
                if message.data.get("new_slot_index") is not None:
                    self.move_slot(message.data)
            elif message.type == PlayerMessageTypeEnum.HAND_ACTION:
                if message.player == self.active_player:
                    await self.poccess_players_move(message.data)
            elif message.type == PlayerMessageTypeEnum.UNKNOWN:
                continue

    async def add_player(self, player: BlackJackPlayer):
        self.all_players.append(player)
        self.send_update_partial(player)

        if self.game_status == "waiting":
            self.game_status = "game_running"
            self._game_running.set()
            
    async def remove_player(self, player: BlackJackPlayer):
        self.all_players.remove(player)
        if len(self.all_players) == 0:
            self.shutdown_game()
        self.send_update_partial()

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
                if self.active_hand.is_busted:
                    self._next_hand.set()
            if action == "stand":
                self._next_hand.set()
            if action == "double_down":
                self.active_player.dobule_down_hand(self.active_hand, self.deck.get_card())
                self._next_hand.set()
            if action == "split":
                self.active_player.split_hand(self.active_hand, self.deck.get_card())
            self.send_update_partial()

    def shutdown_game(self):
        print("Game shut down")
        self.game_status = "waiting"
        self._game_running.clear()
        for running_task in self.running_tasks:
            if running_task != self.game_worker_task:
                running_task.cancel()

    def send_update_partial(self, player: Optional[BlackJackPlayer] = None):
        game_state = GameState.build_partial(self)
        if player is not None:
            player.send(game_state)
        else:
            for temp_player in self.all_players:
                temp_player.send(game_state)
    
    def send_update_full(self, player: Optional[BlackJackPlayer] = None):
        game_state = GameState.build_full(self)
        if player is not None:
            player.send(game_state)
        else:
            for temp_player in self.all_players:
                temp_player.send(game_state)

    async def game_phase(self):
        # game_move_phase >> game_deal_phase >> game_action_phase >> end_phase
        while True:
            if self._game_running.is_set() is False:
                await self._game_running.wait()
            
            elif self.game_status == "game_move_phase":
                await self.game_move_phase()
                self.game_status = "game_deal_phase"

            elif self.game_status == "game_deal_phase":
                pass
                await self.game_deal_phase()
                self.game_status = "game_action_phase"

            elif self.game_status == "game_action_phase":
                pass
                await self.game_action_phase()
                self.game_status = "end_phase"

            elif self.game_status == "end_phase":
                pass
                await self.game_end_phase()
                self.game_status = "game_move_phase"