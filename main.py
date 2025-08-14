from enum import StrEnum
import random


class NoMoreCardsError(Exception):
    pass


class CardNotInDeckError(Exception):
    pass


class CantCompareObjectError(Exception):
    pass


class CardSuit(StrEnum):
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"


class Card:
    def __init__(self, suit, rank) -> None:
        self.suit = suit
        self.rank = rank

    def __str__(self) -> str:
        return f"{self.rank} ({self.suit})"

    def __repr__(self):
        return str(self)

    def __eq__(self, value) -> bool:
        if not isinstance(value, Card):
            raise CantCompareObjectError
        return self.rank == value.rank and self.suit == value.suit


class Deck:
    def __init__(self) -> None:
        self.card_deck = self.build_deck()
        self.shuffle()

    def __len__(self) -> int:
        return len(self.card_deck)

    def get_card(self) -> Card:
        if self.card_deck:
            return self.card_deck.pop()
        raise NoMoreCardsError

    def get_specific_card(self, chosen_card) -> Card:
        for index, card in enumerate(self.card_deck):
            if card == chosen_card:
                self.card_deck.pop(index)
                return card

        raise CardNotInDeckError

    def shuffle(self) -> None:
        random.shuffle(self.card_deck)

    def reset_cards(self) -> None:
        self.card_deck = self.build_deck()

    @staticmethod
    def build_deck() -> list[Card]:
        card_deck = []
        suits = [
            CardSuit.HEARTS,
            CardSuit.DIAMONDS,
            CardSuit.CLUBS,
            CardSuit.SPADES,
        ]
        ranks = list(range(2, 11)) + ["A", "J", "Q", "K"]
        for suit in suits:
            for rank in ranks:
                card_deck.append(Card(suit, rank))
        return card_deck


class BasePlayer:
    def __init__(self) -> None:
        self.hand: list[Card] = []
        self.hand_value = 0

    def display_hand(self):
        pass

    def display_hand_value(self):
        print(f"Value : {self.hand_value}")

    def add_card(self, card):
        self.hand.append(card)
        self.calculate_hand_value()

    def calculate_hand_value(self):
        self.hand_value = 0
        for card in self.hand:
            if card.rank in ["J", "Q", "K"]:
                self.hand_value += 10
            elif card.rank in list(range(2, 11)):
                self.hand_value += int(card.rank)
            else:
                if self.hand_value + 11 > 21:
                    self.hand_value += 1
                else:
                    self.hand_value += 11


class Player(BasePlayer):

    def display_hand(self):
        print(f"Player : {self.hand}")


class House(BasePlayer):

    def display_hand_partial(self):
        print(f"House : {[self.hand[0], '?']}")


class Game:
    def __init__(self, playerNumber: int = 1) -> None:
        self.players: list[Player] = []
        for _ in range(playerNumber):
            self.players.append(Player())
        self.house = House()
        self.deck = Deck()
        self.deck.shuffle()

    def start_round(self):
        for _ in range(2):
            for player in self.players:
                player.add_card(self.deck.get_card())
            self.house.add_card(self.deck.get_card())

    def display_round(self):
        self.house.display_hand_partial()
        for player in self.players:
            player.display_hand()
            
    def determin_round_winners(self):
        winner_list = []
        for player in self.players:
            if player.hand_value < 22:
                if self.house.hand_value > 21:
                    winner_list.append(player)
                else:
                    if player.hand_value > self.house.hand_value:
                        winner_list.append(player)

if __name__ == "__main__":
    game = Game(1)

    game.start_round()
    game.display_round()
    