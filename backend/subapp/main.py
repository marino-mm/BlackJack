import asyncio
import hashlib
from asyncio import Queue, QueueFull

from fastapi import FastAPI
from starlette.websockets import WebSocket, WebSocketDisconnect

game_app = FastAPI()


class UserConnection:
    def __init__(self, websocket: WebSocket):
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
                    message['user'] = f"{self.username}"
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
        self.table_slots = [None, None, None, None, None]
        self.game_Queue = Queue(100)

    def add_listener(self, listener):
        print("Listener added")
        listener.parent_Queue = self.game_Queue
        self.listening_players.append(listener)

    def remove_listener(self, listener):
        self.listening_players.remove(listener)

    async def move_slot(self, message):
        user = message.get('user')
        new_slot = message.get('new_slot_index')
        old_index = None

        for index, slot in enumerate(self.table_slots):
            if slot is not None:
                if slot.get('name') == user:
                    old_index = index

        target_slot = self.table_slots[new_slot]
        if target_slot is None or target_slot.get('name') == "Empty":
            self.table_slots[new_slot] = {'name': user, 'hands': [[]]}
            if old_index is not None:
                self.table_slots[old_index] = {'name': "Empty", "hands": [[]]}

    async def game_queue_worker(self, filter_player = None):
        print("Game queue worker started")
        try:
            while True:
                message = await self.game_Queue.get()
                print(message)
                # print(f"Game Queue processed this message: {message}")
                if filter_player:
                    print(f"message username: {message.get('user')}, filter_player: {filter_player.username}")
                    if message.get('user') == filter_player.username:
                        # Process players move
                        await self.send_json_to_all(message)
                        pass
                elif message.get('messageType') == 'MoveSlot':
                    await self.move_slot(message)
                    await self.send_json_to_all({'messageType': 'MoveSlot', 'slot_list': self.table_slots})
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
                print(listener.connection)
                await self.send_json_to_user(listener, data)
            except Exception as e:
                print(e)
                # print(index)
                pass
                # self.remove_listener(listener)


    async def game_waiting_for_players_to_sit(self):
        for player in self.listening_players:
            player.SEND_MESSAGE_TO_PARENT = True
        task = asyncio.create_task(self.game_queue_worker(), name='game_waiting_for_players_to_sit')
        await asyncio.sleep(10)
        task.cancel()
        for player in self.listening_players:
            player.SEND_MESSAGE_TO_PARENT = False

    async def game_waiting_for_players_move(self, player):
        player.SEND_MESSAGE_TO_PARENT = True
        task = asyncio.create_task(self.game_queue_worker(player), name='waiting_for_players_move')
        await asyncio.sleep(30)
        task.cancel()
        for player in self.listening_players:
            player.SEND_MESSAGE_TO_PARENT = False

    async def start_game(self):
        print("Game started")
        self.STATUS = 'Playing'
        # worker = asyncio.create_task(self.game_queue_worker())
        await asyncio.sleep(1)
        await self.game_waiting_for_players_to_sit()
        for slot in reversed(self.table_slots.copy()):
            if slot is None:
                continue
            player_name = slot['name']
            player = None
            for temp in self.listening_players:
                if temp.username == player_name:
                    player = temp
            await self.game_waiting_for_players_move(player)
        print("Game ended")
        # player_index = 0
        # while player_index < len(self.listening_players):
        #     player = self.listening_players[player_index]
        #     try:
        #         while True:
        #             if player.user_Status != 'Connected':
        #                 raise WebSocketDisconnect
        #             message = asyncio.wait_for(player.message_Queue.get(), 30)
        #             await self.send_json_to_all(message)
        #     except Exception as e:
        #         self.remove_listener(player)
        #         self.STATUS = ''
        #         print(f"Error u start_game-u{e}")


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
