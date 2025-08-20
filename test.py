import unittest
from model import Hand, Card, CardSuit, Game

class TestHand(unittest.TestCase):

    def setUp(self):
        self.hand = Hand()

    def test_value_with_two_aces(self):
        self.hand.add_card(Card(CardSuit.CLUBS, 'A'))
        self.hand.add_card(Card(CardSuit.CLUBS, 'A'))
        expected_value = 12
        self.assertEqual(self.hand.hand_value, expected_value)

    def test_value_with_one_ace(self):
        self.hand.add_card(Card(CardSuit.CLUBS, 'A'))
        self.hand.add_card(Card(CardSuit.CLUBS, '5'))
        expected_value = 16
        self.assertEqual(self.hand.hand_value, expected_value)

    def test_value_with_two_aces_and_eight(self):
        self.hand.add_card(Card(CardSuit.CLUBS, 'A'))
        self.hand.add_card(Card(CardSuit.CLUBS, 'A'))
        self.hand.add_card(Card(CardSuit.CLUBS, '8'))
        expected_value = 20
        self.assertEqual(self.hand.hand_value, expected_value)

    def test_value_with_one_ace_and_two_sevens(self):
        self.hand.add_card(Card(CardSuit.CLUBS, 'A'))
        self.hand.add_card(Card(CardSuit.CLUBS, '7'))
        self.hand.add_card(Card(CardSuit.CLUBS, '7'))
        expected_value = 15
        self.assertEqual(self.hand.hand_value, expected_value)

    def test_value_with_no_tens(self):
        self.hand.add_card(Card(CardSuit.CLUBS, '6'))
        self.hand.add_card(Card(CardSuit.CLUBS, '3'))
        expected_value = 9
        self.assertEqual(self.hand.hand_value, expected_value)

    def test_value_with_tens_and_face(self):
        self.hand.add_card(Card(CardSuit.CLUBS, 'K'))
        self.hand.add_card(Card(CardSuit.CLUBS, '10'))
        expected_value = 20
        self.assertEqual(self.hand.hand_value, expected_value)

    def test_value_with_two_face_cards(self):
        self.hand.add_card(Card(CardSuit.CLUBS, 'K'))
        self.hand.add_card(Card(CardSuit.CLUBS, 'Q'))
        expected_value = 20
        self.assertEqual(self.hand.hand_value, expected_value)
        
    def test_hand_status_playing(self):
        self.hand.add_card(Card(CardSuit.CLUBS, 'K'))
        self.hand.add_card(Card(CardSuit.CLUBS, 'Q'))
        expecter_staus = 'PLAYING'
        self.assertEqual(self.hand.hand_status, expecter_staus)

    def test_hand_status_busted(self):
        self.hand.add_card(Card(CardSuit.CLUBS, 'K'))
        self.hand.add_card(Card(CardSuit.CLUBS, 'Q'))
        self.hand.add_card(Card(CardSuit.CLUBS, '5'))
        expecter_staus = 'BUSTED'
        self.assertEqual(self.hand.hand_status, expecter_staus)
    
    def test_hand_status_blackjack(self):
        self.hand.add_card(Card(CardSuit.CLUBS, 'K'))
        self.hand.add_card(Card(CardSuit.CLUBS, 'A'))
        expecter_staus = 'BLACK_JACK'
        self.assertEqual(self.hand.hand_status, expecter_staus)
    
    def test_hand_status_blackjack_2(self):
        self.hand.add_card(Card(CardSuit.CLUBS, '10'))
        self.hand.add_card(Card(CardSuit.CLUBS, 'A'))
        expecter_staus = 'BLACK_JACK'
        self.assertEqual(self.hand.hand_status, expecter_staus)
        

class TestGame(unittest.TestCase):
    
    def setUp(self):
        self.game = Game(1)
        self.game.players[0].score = 0
        self.game.players[0].hands.append(Hand(100))
        self.game.house.hands.append(Hand())
        
    def test_player_win(self):
        self.game.players[0].hands[0].add_card(Card(CardSuit.CLUBS, 'K'))
        self.game.players[0].hands[0].add_card(Card(CardSuit.CLUBS, 'J'))
        
        self.game.house.hands[0].add_card(Card(CardSuit.CLUBS, '8'))
        self.game.house.hands[0].add_card(Card(CardSuit.CLUBS, '8'))
        
        self.game.end_round()
        
        self.assertEqual(self.game.players[0].score, 200)
    
    def test_player_win_with_blackjack(self):
        self.game.players[0].hands[0].add_card(Card(CardSuit.CLUBS, 'K'))
        self.game.players[0].hands[0].add_card(Card(CardSuit.CLUBS, 'A'))
        
        self.game.house.hands[0].add_card(Card(CardSuit.CLUBS, '8'))
        self.game.house.hands[0].add_card(Card(CardSuit.CLUBS, '8'))
        
        self.game.end_round()
        
        self.assertEqual(self.game.players[0].score, 250)
        
    def test_player_push(self):
        self.game.players[0].hands[0].add_card(Card(CardSuit.CLUBS, 'K'))
        self.game.players[0].hands[0].add_card(Card(CardSuit.CLUBS, 'A'))
        
        self.game.house.hands[0].add_card(Card(CardSuit.CLUBS, 'K'))
        self.game.house.hands[0].add_card(Card(CardSuit.CLUBS, 'A'))
        
        self.game.end_round()
        
        self.assertEqual(self.game.players[0].score, 100)
        
    def test_player_loses(self):
        self.game.players[0].hands[0].add_card(Card(CardSuit.CLUBS, '2'))
        self.game.players[0].hands[0].add_card(Card(CardSuit.CLUBS, '2'))
        
        self.game.house.hands[0].add_card(Card(CardSuit.CLUBS, 'K'))
        self.game.house.hands[0].add_card(Card(CardSuit.CLUBS, 'A'))
        
        self.game.end_round()
        
        self.assertEqual(self.game.players[0].score, 0)
        
if __name__ == '__main__':
    unittest.main()