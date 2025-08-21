from abc import ABC
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


CARD_RANK_ORDER = {
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "J": 11,
    "Q": 12,
    "K": 13,
    "A": 14,
}


class Card:
    def __init__(self, suit, rank) -> None:
        self.suit = suit
        self.rank = rank

    def __str__(self) -> str:
        return f"{self.rank} ({self.suit})"

    def __repr__(self):
        return str(self)

    def __lt__(self, other):
        return CARD_RANK_ORDER[self.rank] < CARD_RANK_ORDER[other.rank]

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
        ranks = list(map(str, range(2, 11))) + ["A", "J", "Q", "K"]
        for suit in suits:
            for rank in ranks:
                card_deck.append(Card(suit, rank))
        return card_deck


class Hand:
    def __init__(self, bid: int = 0) -> None:
        self.bid = bid
        self.cards: List[Card] = []
        self.hand_value = 0
        self.hand_status = "PLAYING"

    def __str__(self) -> str:
        return f"{self.cards}, Value :{self.hand_value})"

    def __repr__(self):
        return str(self)

    def is_busted(self) -> bool:
        return self.hand_status == "BUSTED"

    def is_black_jack(self) -> bool:
        return self.hand_status == "BLACK_JACK"

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
        card_rank_list = []
        self.cards = sorted(self.cards)
        for card in self.cards:
            card_rank_list.append(card.rank)
            if card.rank in ["J", "Q", "K", "10"]:
                self.hand_value += 10
            elif card.rank in list(map(str, range(2, 10))):
                self.hand_value += int(card.rank)
            else:
                if self.hand_value + 11 > 21:
                    self.hand_value += 1
                else:
                    self.hand_value += 11
        if self.hand_value > 21:
            self.hand_status = "BUSTED"

        if len(card_rank_list) == 2:
            if "A" in card_rank_list and self.hand_value == 21:
                self.hand_status = "BLACK_JACK"


class BasePlayer(ABC):
    def __init__(self) -> None:
        self.hands: list[Hand] = []

    def display_hand(self, index: int = 0) -> None:
        print(f"{self.hands[index]}")

    def display_hands(self) -> None:
        print(f"{self.hands}")

    def hit_hand(self, hand: Hand, card) -> None:
        hand.add_card(card)

    def split_hand(self, hand: Hand) -> None:
        if hand.cards[0].rank == hand.cards[1].rank and self.score > hand.bid:
            self.hands.append(Hand(hand.bid))
            card = hand.cards.pop()
            self.hands[-1].add_card(card)
            self.score -= hand.bid
            print("You have succesfully splited your hand!")
        else:
            print("You can't split your hand!")

    def dobule_down_hand(self, hand: Hand, card: Card) -> None:
        if self.score > hand.bid:
            self.score -= hand.bid
            hand.bid *= 2
            hand.add_card(card)
            print("You have successfully double downed your hand!")
        else:
            print("You can't double down hand!")


class Player(BasePlayer):
    def __init__(self, score: int = 100) -> None:
        super().__init__()
        self.score = score

    def display_hands(self) -> None:
        print(f"Player :{self.hands}")

    def __str__(self) -> str:
        return f"Score :{self.score}, Hands :{self.hands}"

    def __repr__(self):
        return str(self)


class House(BasePlayer):

    def display_hand_partial(self):
        print(f"House :{[self.hands[0].cards[0], '?']}")


class Game:
    def __init__(self, player_number: int = 1) -> None:
        self.players: list[Player] = []
        for _ in range(player_number):
            self.players.append(Player())
        self.house = House()
        self.deck = Deck()
        self.deck.shuffle()

    def round_setup(self) -> None:
        for player in self.players:
            hand_numb = input("Hand number: ")
            while not hand_numb.isnumeric() or int(hand_numb) > 4:
                print("Invalid Hand Number, try again.")

            for hand_index, _ in enumerate(range(int(hand_numb))):
                hand_bid = input(f"Input Hand {hand_index + 1} Bid: ")

                while True:
                    if not hand_bid.isnumeric():
                        print("Invalid Hand Bid, try again.")
                    elif int(hand_bid) > player.score:
                        print("Bid is too high, try again.")
                    elif int(-1) > player.score:
                        print("Hand canceled.")
                        break
                    else:
                        hand_bid = int(hand_bid)
                        player.hands.append(Hand(hand_bid))
                        player.score -= hand_bid
                        break
        self.house.hands.append(Hand())

    def end_round(self) -> None:
        house_hand = self.house.hands[0]
        for player in self.players:
            for hand in player.hands:
                if hand.is_busted() and house_hand.is_busted():
                    player.score += hand.bid
                elif house_hand.is_busted():
                    player.score += hand.bid * 2
                    if hand.is_black_jack():
                        player.score += int(round(hand.bid * 0.5, 0))
                else:
                    if hand.hand_value == house_hand.hand_value:
                        player.score += hand.bid
                    elif hand.hand_value > house_hand.hand_value:
                        player.score += hand.bid * 2
                        if hand.is_black_jack():
                            player.score += int(round(hand.bid * 0.5, 0))
                    else:
                        pass

    def deal_to_all_hands(self):

        for _ in range(2):
            for player in self.players:
                for hand in player.hands:
                    hand.add_card(self.deck.get_card())
            self.house.hands[0].add_card(self.deck.get_card())

    def house_play_hand(self):
        house = self.house
        hand = self.house.hands[0]
        while hand.hand_value <= 16:
            house.hit_hand(hand, self.deck.get_card())

    def display_round(self):
        self.house.display_hand_partial()
        for player in self.players:
            player.display_hands()

    def display_round_end(self):
        self.house.display_hand()
        for player in self.players:
            player.display_hands()

    def play_round(self):
        self.round_setup()
        self.deal_to_all_hands()

        for player_index, player in enumerate(self.players):
            hand_index = 0
            while hand_index < len(player.hands):
                hand = player.hands[hand_index]
                TURN_STATUS = "PLAYING"
                while True:
                    if TURN_STATUS == "PLAYING":
                        print(f"House: {self.house.hands[0].get_partial_hand_str()}")
                        print(f"Player: {hand.cards}")
                        print(f"What will player {player_index + 1} do?\n1) Hit\n2) Stand\n3) Double down\n4) Split")
                        move = input("Your move: ")
                        if move == "1":
                            player.hit_hand(hand, self.deck.get_card())
                            if hand.is_busted():
                                print("You hand is busted!")
                                player.display_hand()
                                TURN_STATUS = "STANDING"
                        if move == "2":
                            TURN_STATUS = "STANDING"
                        if move == "3":
                            player.dobule_down_hand(hand, self.deck.get_card())
                            if hand.is_busted():
                                print("You hand is busted!")
                            TURN_STATUS = "STANDING"
                        if move == "4":
                            player.split_hand(hand)
                    elif TURN_STATUS == "STANDING":
                        print("Your turn ended")
                        break
                hand_index += 1
        self.house_play_hand()
        print("\n\n\n")
        self.end_round()
        self.display_round_end()
        for player in self.players:
            print(player)
