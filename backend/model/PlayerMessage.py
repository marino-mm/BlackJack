from enum import Enum, auto
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .BlackJackGame import BlackJackGame
    from .BlackJackPlayer import BlackJackPlayer

class PlayerMessageTypeEnum(Enum):
    JOIN = auto()
    DISCONNECT = auto()
    MOVE = auto()
    HAND_ACTION = auto()
    UNKNOWN = auto()


class PlayerMessage:
    player: "BlackJackPlayer"
    game: "BlackJackGame"
    type: PlayerMessageTypeEnum
    data: Optional[dict]

    def __init__(self, player, game, type_str, data: Optional[dict] = None):
        self.player = player
        self.game = game
        self.data = data
        
        type_mapping = {
            "MoveSlot": PlayerMessageTypeEnum.MOVE,
            "Action": PlayerMessageTypeEnum.HAND_ACTION,
            "Join": PlayerMessageTypeEnum.JOIN,
            "Disconnect": PlayerMessageTypeEnum.DISCONNECT,
        }
        self.type = type_mapping.get(type_str, PlayerMessageTypeEnum.UNKNOWN)