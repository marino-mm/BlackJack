from enum import StrEnum
import random
from typing import List


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
        self.hands: list[Hand] = [Hand()]

    def display_hand(self, index: int = 0) -> None:
        print(f"{self.hands[index]}")

    def display_hands(self) -> None:
        print(f"{self.hands}")

class Player(BasePlayer):

    def display_hands(self) -> None:
        print(f"Player :{self.hands}")


class House(BasePlayer):

    def display_hand_partial(self):
        print(f"House :{[self.hands[0].cards[0], '?']}")

class Hand:
    def __init__(self) -> None:
        self.cards: List[Card] = []
        self.hand_value = 0

    def __str__(self) -> str:
        return f"{self.cards})"

    def __repr__(self):
        return str(self)

    def display_hand(self):
        print(self.cards)

    def get_partial_hand_str(self):
        return f"{[self.cards[0], '?']}"

    def get_hand_str(self):
        return f"{[self.cards]}"

    def add_card(self, card):
        self.cards.append(card)
        self.calculate_hand_value()

    def return_card(self, card):
        card = self.cards.pop()
        self.calculate_hand_value()
        return card

    def calculate_hand_value(self):
        self.hand_value = 0
        for card in self.cards:
            if card.rank in ["J", "Q", "K"]:
                self.hand_value += 10
            elif card.rank in list(range(2, 11)):
                self.hand_value += int(card.rank)
            else:
                if self.hand_value + 11 > 21:
                    self.hand_value += 1
                else:
                    self.hand_value += 11

class Game:
    def __init__(self, player_number: int = 1) -> None:
        self.players: list[Player] = []
        for _ in range(player_number):
            self.players.append(Player())
        self.house = House()
        self.deck = Deck()
        self.deck.shuffle()

    def start_round(self):
        for _ in range(2):
            for player in self.players:
                player.hands[0].add_card(self.deck.get_card())
            self.house.hands[0].add_card(self.deck.get_card())

    def display_round(self):
        self.house.display_hand_partial()
        for player in self.players:
            player.display_hands()

    def display_round_end(self):
        self.house.display_hand()
        for player in self.players:
            player.display_hands()


def test():
    game = Game(3)
    game.start_round()
    for index, player in enumerate(game.players):
        hand_index = 0
        while hand_index < len(player.hands):
            hand = player.hands[hand_index]
            TURN_STATUS = "PLAYING"
            while True:
                if TURN_STATUS == "PLAYING":
                    print(f"House: {game.house.hands[0].get_partial_hand_str()}")
                    print(f"Player: {hand.get_hand_str()}")
                    print(f"What will player {index} do?\n1) Hit\n2) Stand\n3) Double down\n4) Split")
                    move = input("Your move: ")
                    if move == "1":
                        player.hands[0].add_card(game.deck.get_card())
                        if player.hands[0].hand_value > 21:
                            print("You have busted!")
                            player.display_hand()
                            TURN_STATUS = "STANDING"
                    if move == "2":
                        TURN_STATUS = "STANDING"
                    if move == "3":
                        player.hands[0].add_card(game.deck.get_card())
                        TURN_STATUS = "STANDING"
                    if move == "4":
                        if hand.cards[0].rank == hand.cards[1].rank:
                            player.hands.append(Hand())
                            card = player.hand[hand_index].cards.pop()
                            player.hands[-1].add_card(card)
                            print("You have succesfully splited your hand!")
                        else:
                            print("You cant split your hand!")
                elif TURN_STATUS == "STANDING":
                    print("Your turn ended")
                    break
            hand_index += 1
    print("\n\n\n")
    game.display_round_end()
    # input("Game ended!")

if __name__ == "__main__":
    test()