from dataclasses import dataclass
from enum import Enum, auto

from backend.subapp.temp_BlackJack import BlackJackGame, BlackJackPlayer


class PlayerMessageTypeEnum(Enum):
    JOIN = auto()
    DISCONNECT = auto()
    MOVE = auto()
    HAND_ACTION = auto()


@dataclass
class PlayerMessage:
    player: BlackJackPlayer
    game: BlackJackGame
    type: PlayerMessageTypeEnum
    data: dict
