

from dataclasses import dataclass
from typing import List
# from BlackJack_app import BlackJackGame


@dataclass
class PlayerMessage:
    player: int

    def execute(self):
        pass


@dataclass
class PlayerMessageJoin(PlayerMessage):
    pass

    def execute(self):
        print("PlayerMessageJoin")


@dataclass
class PlayerMessageLeave(PlayerMessage):
    pass

    def execute(self):
        print("PlayerMessageLeave")


@dataclass
class PlayerMessageMoveSeat(PlayerMessage):
    seat_index: int

    def execute(self):
        print("PlayerMessageMoveSeat")


@dataclass
class PlayerMessageHandAction(PlayerMessage):
    action: str

    def execute(self):
        print("PlayerMessageHandAction")


@dataclass
class Test:

    @staticmethod
    def test():
        message_list: List[PlayerMessage] = [
            PlayerMessageJoin(0),
            PlayerMessageLeave(0),
            PlayerMessageMoveSeat(0, 0),
            PlayerMessageHandAction(0, 'hit'),
        ]
        for m in message_list:
            m.execute()


Test().test()


# class BlackJackGame_ext(BlackJackGame):

#     async def game_worker(self):
#         while True:
#             message_dict = await self.game_queue.get()

#     async def player_move_task(self):
#         while True:
#             message_dict = await self.game_queue.get()
#             if self.game_status == "game_move_phase":
#                 if message_dict.get("new_slot_index") is not None:
#                     self.move_slot(message_dict)
#                     await self.send_slots()

#     async def player_action_task(self):
#         while True:
#             message_dict = await self.game_queue.get()
#             if self.game_status == "game_action_phase":
#                 if message_dict.get("player", None) == self.active_player:
#                     valid_move = await self.poccess_players_move(message_dict)
#                     if valid_move:
#                         await self.send_slots()
#                         return True
