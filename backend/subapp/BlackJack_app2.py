from asyncio import CancelledError
from fastapi import FastAPI, WebSocket

from backend.model.BlackJackGame import BlackJackGame
from backend.model.BlackJackPlayer import BlackJackPlayer
from backend.model.PlayerMessage import PlayerMessage, PlayerMessageTypeEnum


BlackJack = FastAPI()

game = BlackJackGame()


@BlackJack.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    blackjack_player = None
<<<<<<< HEAD
    try:
        await ws.accept()
        blackjack_player = await BlackJackPlayer.player_creation_cls(ws, game)
        await game.add_player(blackjack_player)
        await blackjack_player.ping_pong_task
=======
    # print("here")
    try:
        await ws.accept()
        blackjack_player = await BlackJackPlayer.player_creation_cls(ws, game)
        await game.game_queue.put(PlayerMessage(blackjack_player, game, PlayerMessageTypeEnum.JOIN, None))
        # await game.add_player(blackjack_player)
        await blackjack_player.websocket_ping_pong()
>>>>>>> 525d907e29d2c7f7a7ddfecf7a8eaa073a75a079
    except CancelledError:
        print("Cancelled Error in websocket_endpoint")
    except Exception as e:
        print(f"Exception happened in websocket_endpoint, exception: {e}. Disconnecting player")
        if blackjack_player:
            await blackjack_player.disconnect_player()
