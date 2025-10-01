

from dataclasses import dataclass
from backend.subapp.BlackJack_app import BlackJackGame, BlackJackPlayer

@dataclass
class PlayerMessage:
    player: BlackJackPlayer



class BlackJackGame_ext(BlackJackGame):
    
    
    async def game_worker(self):
        while True:
            message_dict = await self.game_queue.get()
    
    
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