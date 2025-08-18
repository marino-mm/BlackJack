from model import Hand, Game

def test():
    game = Game(1)
    game.round_setup()
    game.deal_to_all_hands()
    for player_index, player in enumerate(game.players):
        hand_index = 0
        while hand_index < len(player.hands):
            hand = player.hands[hand_index]
            TURN_STATUS = 'PLAYING'
            while True:
                if TURN_STATUS == "PLAYING":
                    print(f"House: {game.house.hands[0].get_partial_hand_str()}")
                    # print(f"Player: {hand.get_hand_str()}")
                    print(f"Player: {hand.cards}")
                    print(f"What will player {player_index + 1} do?\n1) Hit\n2) Stand\n3) Double down\n4) Split")
                    move = input("Your move: ")
                    if move == "1":
                        player.hands[0].add_card(game.deck.get_card())
                        if player.hands[0].hand_value > 21:
                            print("You hand is have busted!")
                            player.display_hand()
                            TURN_STATUS = "STANDING"
                    if move == "2":
                        TURN_STATUS = "STANDING"
                    if move == "3":
                        player.dobule_down_hand(hand, game.deck.get_card())
                        TURN_STATUS = "STANDING"
                    if move == "4":
                        player.split_hand(hand)
                elif TURN_STATUS == "STANDING":
                    print("Your turn ended")
                    break
            hand_index += 1
    print("\n\n\n")
    game.end_round()
    game.display_round_end()
    # input("Game ended!")

def test2():
    game = Game(1)
    game.play_round()
    print("End")

if __name__ == "__main__":
    test2()

