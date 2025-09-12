import asyncio
import hashlib
from asyncio import Queue, QueueFull
from typing import List

from fastapi import FastAPI
from starlette.websockets import WebSocket, WebSocketDisconnect

from backend.model.BlackJack_game_models import Deck, House, Hand, Player

game_app = FastAPI()


class UserConnection(Player):
    def __init__(self, websocket: WebSocket):
        super().__init__()
        self.connection = websocket
        self.username = None
        self.message_Queue = Queue(10)
        self.Ping_Pong_Queue = Queue(1)
        self.user_Status = None
        self.parent_Queue = None
        self.SEND_MESSAGE_TO_PARENT = False

    async def create(self):
        while not self.username:
            message_dict = await self.connection.receive_json()
            if message_dict.get('username'):
                self.username = message_dict.get('username')
        self.user_Status = 'Connected'

    async def start_listening(self):
        try:
            while True:
                message = await self.connection.receive_json()
                if message.get('messageType') == 'PingPong':
                    self.Ping_Pong_Queue.put_nowait(message)
                elif self.parent_Queue and self.SEND_MESSAGE_TO_PARENT:
                    # message['user'] = f"{self.username}"
                    message['user'] = self
                    self.parent_Queue.put_nowait(message)
                else:
                    self.message_Queue.put_nowait(message)
        except WebSocketDisconnect:
            print('Websocket disconnected')
            self.user_Status = 'Disconnected'
        except asyncio.CancelledError:
            print('Listening task cancelled')
            self.user_Status = 'Disconnected'
            raise
        except QueueFull:
            pass

    def frontend_dict(self):
        return {
            'name': self.username,
            'hands': [hand.json_hand() for hand in self.hands],
        }

    def __eq__(self, value: object) -> bool:
        if isinstance(value, UserConnection):
            return self.username == value.username
        return False

    def __hash__(self):
        return hash((self.username, self.connection))

    def __str__(self):
        return self.username

    def __repr__(self):
        return str(self)



class GameTable:
    def __init__(self):
        self.listening_players = []
        self.STATUS = ''
        self.table_slots:List[UserConnection|None] = [None, None, None, None, None]
        self.game_Queue = Queue(100)
        self.deck = Deck()
        self.house = House()

    def add_listener(self, listener):
        print("Listener added")
        listener.parent_Queue = self.game_Queue
        self.listening_players.append(listener)

    def remove_listener(self, listener):
        self.listening_players.remove(listener)

    async def move_slot(self, message):
        user:UserConnection = message.get('user')
        new_slot = message.get('new_slot_index')
        try:
            old_index = self.table_slots.index(user)
        except ValueError:
            old_index = None
        target_slot = self.table_slots[new_slot]
        if target_slot is None:
            self.table_slots[new_slot] = user
            if old_index is not None:
                self.table_slots[old_index] = None

    async def game_queue_worker(self, filter_player: UserConnection | None = None, hand = None):
        print("Game queue worker started")
        try:
            while True:
                message = await self.game_Queue.get()
                if filter_player:
                    # if message.get('user').username == filter_player.username:
                    if message.get('user') == filter_player:
                        # Process players move
                        if message.get('messageType') == 'Action':
                            if message.get('message') == 'hit':
                                filter_player.hit_hand(hand, self.deck.get_card())
                            if message.get('message') == 'stand':
                                return 'Player action was stand'
                            if message.get('message') == 'double_down':
                                filter_player.dobule_down_hand(hand, self.deck.get_card())
                                return 'Player action was double_down'
                            if message.get('message') == 'split':
                                filter_player.split_hand(hand)
                        # await self.send_json_to_all(message)
                        await self.send_json_to_all({'messageType': 'UpdateSlots',
                                                     'slot_list': [x.frontend_dict() if x is not None else None for x in
                                                                   self.table_slots]})
                        # for send_data in self.table_slots:
                        pass
                elif message.get('messageType') == 'MoveSlot':
                    await self.move_slot(message)
                    await self.send_json_to_all({'messageType': 'UpdateSlots', 'slot_list': [x.frontend_dict() if x is not None else None for x in self.table_slots]})
                else:
                    # Do nothing if it is not players message
                    pass
        except Exception as e:
            print(f"game_Queue_worker: {e}")

    async def send_json_to_user(self, listener, data):
        await listener.connection.send_json(data)

    async def send_json_to_all(self, data):
        for index, listener in enumerate(self.listening_players):
            try:
                await self.send_json_to_user(listener, data)
            except Exception as e:
                print(e)

    async def game_waiting_for_players_to_sit(self):
        for player in self.listening_players:
            player.SEND_MESSAGE_TO_PARENT = True
        task = asyncio.create_task(self.game_queue_worker(), name='game_waiting_for_players_to_sit')
        await asyncio.sleep(5)
        task.cancel()
        for player in self.listening_players:
            player.SEND_MESSAGE_TO_PARENT = False

    async def game_waiting_for_players_move_per_hand(self, player):
        player.SEND_MESSAGE_TO_PARENT = True
        hand_index = 0
        while len(player.hands) < hand_index:
        # for hand in player.hands:
            hand = player.hands[hand_index]
            task = asyncio.create_task(self.game_queue_worker(player, hand), name='waiting_for_players_move')
            try:
                result = await asyncio.wait_for(task, timeout=30)
                pass
            except asyncio.TimeoutError:
                task.cancel()
            hand_index += 1
        player.SEND_MESSAGE_TO_PARENT = False

    async def start_game(self):
        print("Game started")
        self.STATUS = 'Playing'
        await asyncio.sleep(1)
        await self.game_waiting_for_players_to_sit()
        players_turn_list = reversed(self.table_slots.copy())
        players_turn_list = [player for player in players_turn_list if player is not None]
        for player in players_turn_list:
            player.hands.append(Hand())
            player.hit_hand(player.hands[0], self.deck.get_card())
            player.hit_hand(player.hands[0], self.deck.get_card())

        await self.send_json_to_all({'messageType': 'UpdateSlots','slot_list': [x.frontend_dict() if x is not None else None for x in self.table_slots]})
        for player in reversed(self.table_slots.copy()):
            if player is None:
                continue
            await self.game_waiting_for_players_move_per_hand(player)
        print("Game ended")


async def websocket_ping_pong(ws: UserConnection):
    try:
        await ws.connection.send_json({'messageType': "PingPong", 'message': 'Ping'})
        try:
            message = await asyncio.wait_for(ws.Ping_Pong_Queue.get(), timeout=5)
        except asyncio.TimeoutError:
            print(f"No Pong response from {ws.username}")
            await ws.connection.close(reason='Pong not received')
            raise WebSocketDisconnect

    except WebSocketDisconnect:
        print(f"{ws.username} disconnected due to missing Pong.")
        gameTable.remove_listener(ws)


gameTable = GameTable()


@game_app.websocket('/ws')
async def connect_websocket(websocket: WebSocket):
    try:
        await websocket.accept()
        user = UserConnection(websocket)
        await user.create()
        gameTable.add_listener(user)
        asyncio.create_task(user.start_listening())
        if gameTable.STATUS != 'Playing':
            asyncio.create_task(gameTable.start_game())
        while True:
            await asyncio.sleep(10)
            await websocket_ping_pong(user)

    except Exception as e:
        print(f"Error u game_loop-u{e}")
