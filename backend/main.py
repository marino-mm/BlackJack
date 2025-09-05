from backend.model.BlackJack_game_models import Game

def test2():
    game = Game(1)
    game.play_round()
    # print("End")

if __name__ == "__main__":
    test2()