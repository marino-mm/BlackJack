from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response
from model import Deck

app = FastAPI()

deck = None


@app.get("/deck/generate")
async def get_deck():
    global deck
    if not deck:
        deck = Deck()
    else:
        deck.shuffle()

    return {"message": "Deck created" if not deck else "Deck shuffled"}


@app.get("/deck/get_card")
async def get_card():
    global deck
    if not deck:
        deck = Deck()
    card = deck.get_card()
    return {"card": str(card)}


app.mount("/", StaticFiles(directory="static", html=True), name="static")
