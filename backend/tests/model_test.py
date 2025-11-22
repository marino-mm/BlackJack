import asyncio
import unittest
from backend.model.BlackJackGame import BlackJackGame
from backend.model.BlackJackGameState import GameState


class TestBlackJackGameState(unittest.TestCase):

    def setUp(self):
        self.game_state = GameState(
            event_name='', active_player_username='', slot_list=[None, None, None, None, None], house_hand=[{"cards": []}], time_remaining=30)

    def test_black_jack_game_state_json_serialitation(self):

        json_str = self.game_state.model_dump_json()
        assert isinstance(json_str, str)


if __name__ == "__main__":
    unittest.main()
