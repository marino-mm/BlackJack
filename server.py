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
        deck.reset_cards()

    return {"message": "Deck created" if not deck else "Deck shuffled", "deck": list(map(str, deck.card_deck)) }


@app.get("/deck/get_card")
async def get_card():
    global deck
    if not deck:
        deck = Deck()
    card = deck.get_card()
    return {"card": str(card), "deck": list(map(str, deck.card_deck)) }


app.mount("/", StaticFiles(directory="static", html=True), name="static")
