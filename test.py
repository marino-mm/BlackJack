import unittest
from model import Hand, Card, CardSuit

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

if __name__ == '__main__':
    unittest.main()