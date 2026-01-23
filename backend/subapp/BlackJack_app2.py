from asyncio import CancelledError
from fastapi import FastAPI, WebSocket

from backend.model.BlackJackGame import BlackJackGame
from backend.model.BlackJackPlayer import BlackJackPlayer


BlackJack = FastAPI()

game = BlackJackGame()


@BlackJack.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    blackjack_player = None
    try:
        await ws.accept()
        blackjack_player = await BlackJackPlayer.player_creation_cls(ws, game)
        await game.add_player(blackjack_player)
        await blackjack_player.ping_pong_task
    except CancelledError:
        print("Cancelled Error in websocket_endpoint")
    except Exception as e:
        if blackjack_player:
            await blackjack_player.disconnect_player()
            print(f"Exception happened in websocket_endpoint, exception: {e}")
