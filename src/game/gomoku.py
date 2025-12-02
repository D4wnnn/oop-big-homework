from .base_game import BaseGame
from .player import Player
from .exceptions import InvalidMoveError

class GomokuGame(BaseGame):
    def __init__(self, board_size: int):
        super().__init__(board_size)

    def place_stone(self, row: int, col: int):
        if self.game_over:
            raise InvalidMoveError("Game is already over.")

        if not self.board.is_within_bounds(row, col):
            raise InvalidMoveError("Position out of bounds.")

        if self.board.get(row, col) is not None:
            raise InvalidMoveError("Position already occupied.")

        self.save_state()
        self.board.place_stone(row, col, self.current_player)
        
        winner = self.check_winner_at(row, col)
        if winner:
            self.game_over = True
            self.winner = winner
        elif self.board.is_full():
            self.game_over = True
            self.winner = None # Draw
        else:
            self.switch_player()

    def check_winner(self):
        return self.winner

    def check_winner_at(self, row: int, col: int):
        """Optimized check starting from the last move."""
        player = self.board.get(row, col)
        if not player:
            return None

        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for dr, dc in directions:
            count = 1
            # Check forward
            for i in range(1, 5):
                r, c = row + dr * i, col + dc * i
                if self.board.get(r, c) == player:
                    count += 1
                else:
                    break
            # Check backward
            for i in range(1, 5):
                r, c = row - dr * i, col - dc * i
                if self.board.get(r, c) == player:
                    count += 1
                else:
                    break
            
            if count >= 5:
                return player
        return None
