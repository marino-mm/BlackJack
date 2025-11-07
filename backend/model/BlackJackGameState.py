from typing import List, Optional, TYPE_CHECKING

from pydantic import BaseModel
if TYPE_CHECKING:
    from . import BlackJackGame


class GameState(BaseModel):
    event_name: Optional[str]
    active_player_username: Optional[str]
    slot_list: Optional[List[dict]]
    house_hand: Optional[dict]
    time_remaining: Optional[int]

    @classmethod
    def build_full(cls, game: "BlackJackGame", full_house_hand=False):
        event_name = game.game_title
        active_player_username = game.active_player.player_name if game.active_player is not None else ""
        slot_list = [{"name": player.player_name, "hands": player.hands_json()} if player is not None else None for player in game.sitting_players]
        house_hand = game.house.hands_json()
        time_remaining = game.countdown_time

        return cls(
            event_name=event_name,
            active_player_username=active_player_username,
            slot_list=slot_list,
            house_hand=house_hand,
            time_remaining=time_remaining,
        )

    @classmethod
    def build_partial(cls, game: "BlackJackGame", full_house_hand=False):
        event_name = game.game_title
        active_player_username = game.active_player.player_name if game.active_player is not None else ""
        slot_list = [{"name": player.player_name, "hands": player.hands_json()} if player is not None else None for player in game.sitting_players]
        house_hand = game.house.partial_hand_json()
        time_remaining = game.countdown_time

        return cls(
            event_name=event_name,
            active_player_username=active_player_username,
            slot_list=slot_list,
            house_hand=house_hand,
            time_remaining=time_remaining,
        )

    @classmethod
    def build_countdown_time(cls, game: "BlackJackGame", full_house_hand=False):
        time_remaining = game.countdown_time

        return cls(time_remaining=time_remaining)
