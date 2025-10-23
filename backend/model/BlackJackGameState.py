from typing import List, Optional

from pydantic import BaseModel


class GameState(BaseModel):
    event_name: Optional[str]
    active_player_username: Optional[str]
    slot_list: Optional[List[dict]]
    house_hand: Optional[dict]
    time_remaining: Optional[int]
