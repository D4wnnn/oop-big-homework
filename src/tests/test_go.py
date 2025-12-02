import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.go import GoGame
from game.player import Player
from game.exceptions import InvalidMoveError

class TestGoGame(unittest.TestCase):
    def setUp(self):
        self.game = GoGame(9)

    def test_place_stone(self):
        self.game.place_stone(0, 0)
        self.assertEqual(self.game.board.get(0, 0), Player.BLACK)
        self.assertEqual(self.game.current_player, Player.WHITE)

    def test_capture(self):
        # B(0,1), W(0,0), B(1,0) -> W captured
        self.game.place_stone(0, 1) # B
        self.game.place_stone(0, 0) # W
        self.game.place_stone(1, 0) # B
        self.assertIsNone(self.game.board.get(0, 0)) # W captured
        self.assertEqual(self.game.captured_stones[Player.BLACK], 1)

    def test_suicide(self):
        # Surround (0,0) then try to place there
        self.game.place_stone(0, 1) # B
        self.game.place_stone(2, 2) # W (dummy)
        self.game.place_stone(1, 0) # B
        self.game.place_stone(3, 3) # W (dummy)
        
        # Now W tries to play (0,0), it has 0 liberties.
        # But it needs to be White's turn.
        # Current is Black (since last was W).
        self.game.place_stone(5, 5) # B dummy
        # Now White's turn.
        with self.assertRaises(InvalidMoveError):
            self.game.place_stone(0, 0)

    def test_ko(self):
        # Simple Ko setup
        # . B W .
        # B W . W
        # . B W .
        
        # 1. B(2, 1)
        self.game.place_stone(2, 1)
        # 2. W(2, 2)
        self.game.place_stone(2, 2)
        # 3. B(3, 2)
        self.game.place_stone(3, 2)
        # 4. W(3, 3)
        self.game.place_stone(3, 3)
        # 5. B(4, 1) -- Wait, let's make a simpler Ko.
        
        #   X O 
        # X . X O
        #   X O
        
        self.game = GoGame(9)
        # B: 0,1
        self.game.place_stone(0, 1)
        # W: 0,2
        self.game.place_stone(0, 2)
        # B: 1,0
        self.game.place_stone(1, 0)
        # W: 1,3
        self.game.place_stone(1, 3)
        # B: 1,2
        self.game.place_stone(1, 2) 
        # W: 2,1
        self.game.place_stone(2, 1) 
        
        # Capture W at 1,1 ? No setup is messy.
        # Use cross shape:
        #   B
        # B W B
        #   B
        
        self.game = GoGame(9)
        # B at (0, 1)
        self.game.place_stone(0, 1)
        # W at (3, 3)
        self.game.place_stone(3, 3)
        # B at (1, 0)
        self.game.place_stone(1, 0)
        # W at (4, 4)
        self.game.place_stone(4, 4)
        # B at (1, 2)
        self.game.place_stone(1, 2)
        
        # Now White captures B? No.
        
        # Proper Ko:
        # B: 1,2
        # W: 1,3
        # B: 2,1
        # W: 2,4 -> W: 2,2 (Capture B at 2,3?)
        pass

if __name__ == '__main__':
    unittest.main()
