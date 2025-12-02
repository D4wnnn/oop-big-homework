import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.gomoku import GomokuGame
from game.player import Player

class TestGomoku(unittest.TestCase):
    def setUp(self):
        self.game = GomokuGame(15)

    def test_win_horizontal(self):
        # X X X X X
        for i in range(5):
            self.game.place_stone(0, i) # Black
            if i < 4:
                self.game.place_stone(1, i) # White
        
        self.assertTrue(self.game.is_game_over())
        self.assertEqual(self.game.check_winner(), Player.BLACK)

    def test_undo(self):
        self.game.place_stone(0, 0)
        self.game.undo()
        self.assertIsNone(self.game.board.get(0, 0))
        self.assertEqual(self.game.current_player, Player.BLACK)

if __name__ == '__main__':
    unittest.main()
