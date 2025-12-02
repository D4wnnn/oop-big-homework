from .player import Player
from .exceptions import InvalidBoardSizeError

class Board:
    def __init__(self, size: int):
        if not (8 <= size <= 19):
            raise InvalidBoardSizeError(f"Board size must be between 8 and 19. Got {size}.")
        self.size = size
        # Grid is a list of lists. None represents empty.
        # indexed as grid[row][col]
        self.grid = [[None for _ in range(size)] for _ in range(size)]

    def is_within_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.size and 0 <= col < self.size

    def get(self, row: int, col: int):
        if not self.is_within_bounds(row, col):
            return None 
        return self.grid[row][col]

    def place_stone(self, row: int, col: int, player: Player):
        if self.is_within_bounds(row, col):
            self.grid[row][col] = player

    def remove_stone(self, row: int, col: int):
        if self.is_within_bounds(row, col):
            self.grid[row][col] = None

    def is_full(self) -> bool:
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] is None:
                    return False
        return True

    def clone(self):
        """Create a deep copy of the board."""
        new_board = Board(self.size)
        for r in range(self.size):
            for c in range(self.size):
                new_board.grid[r][c] = self.grid[r][c]
        return new_board

    def __str__(self):
        """Simple string representation for debugging."""
        s = []
        for r in range(self.size):
            row_str = []
            for c in range(self.size):
                p = self.grid[r][c]
                if p is None:
                    row_str.append(".")
                else:
                    row_str.append(p.symbol())
            s.append(" ".join(row_str))
        return "\n".join(s)
