from .base_game import BaseGame
from .player import Player
from .exceptions import InvalidMoveError
import copy

class GoGame(BaseGame):
    def __init__(self, board_size: int):
        super().__init__(board_size)
        self.pass_count = 0
        self.captured_stones = {Player.BLACK: 0, Player.WHITE: 0}
        # History needed for Ko check is already in BaseGame, but we need to ensure it's used correctly.

    def pass_turn(self):
        self.save_state()
        self.pass_count += 1
        if self.pass_count >= 2:
            self.game_over = True
            self.winner = self.calculate_winner()
        self.switch_player()

    def save_state(self):
        """Saves the current state including captured stones and pass count."""
        self.history.append((self.board.clone(), self.current_player, self.captured_stones.copy(), self.pass_count))

    def undo(self):
        """Reverts to the previous state."""
        if not self.history:
            raise InvalidMoveError("No moves to undo.")
        
        prev_board, prev_player, prev_captured, prev_pass = self.history.pop()
        self.board = prev_board
        self.current_player = prev_player
        self.captured_stones = prev_captured
        self.pass_count = prev_pass
        self.game_over = False
        self.winner = None
        return True

    def place_stone(self, row: int, col: int):
        if self.game_over:
            raise InvalidMoveError("Game is already over.")
        
        if not self.board.is_within_bounds(row, col):
            raise InvalidMoveError("Position out of bounds.")

        if self.board.get(row, col) is not None:
            raise InvalidMoveError("Position already occupied.")

        # Tentative move logic
        # Clone the board to test the move
        test_board = self.board.clone()
        test_board.place_stone(row, col, self.current_player)

        # Check captures
        captured_any = False
        stones_captured_count = 0
        opponent = self.current_player.other()
        neighbors = self._get_neighbors(row, col)
        
        for nr, nc in neighbors:
            if test_board.get(nr, nc) == opponent:
                group = self._get_group(nr, nc, test_board)
                if self._count_liberties(group, test_board) == 0:
                    stones_captured_count += len(group)
                    self._remove_group(group, test_board)
                    captured_any = True

        # Check suicide
        my_group = self._get_group(row, col, test_board)
        if self._count_liberties(my_group, test_board) == 0:
            raise InvalidMoveError("Suicide move is not allowed.")

        # Check Ko
        if len(self.history) > 0:
            ko_state = self.history[-1][0]
            if self._boards_equal(test_board, ko_state):
                 raise InvalidMoveError("Ko rule violation.")

        # If valid:
        self.save_state()
        self.board = test_board
        self.captured_stones[self.current_player] += stones_captured_count
        self.pass_count = 0 # Reset pass count on valid move
        self.switch_player()

    def _boards_equal(self, b1, b2):
        # Optimization: just compare grids
        return b1.grid == b2.grid

    def _get_neighbors(self, r, c):
        n = []
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if self.board.is_within_bounds(nr, nc):
                n.append((nr, nc))
        return n

    def _get_group(self, r, c, board):
        color = board.get(r, c)
        group = set()
        stack = [(r, c)]
        group.add((r, c))
        
        while stack:
            curr_r, curr_c = stack.pop()
            neighbors = []
            # logic to find neighbors
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nr, nc = curr_r + dr, curr_c + dc
                if board.is_within_bounds(nr, nc):
                    neighbors.append((nr, nc))

            for nr, nc in neighbors:
                if board.get(nr, nc) == color and (nr, nc) not in group:
                    group.add((nr, nc))
                    stack.append((nr, nc))
        return group

    def _count_liberties(self, group, board):
        liberties = set()
        for r, c in group:
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nr, nc = r + dr, c + dc
                if board.is_within_bounds(nr, nc):
                    if board.get(nr, nc) is None:
                        liberties.add((nr, nc))
        return len(liberties)

    def _remove_group(self, group, board):
        for r, c in group:
            board.remove_stone(r, c)

    def calculate_winner(self):
        # Simple Area Scoring
        # Score = Stones on board + Territory
        black_score = 0
        white_score = 0
        
        visited = set()

        for r in range(self.board_size):
            for c in range(self.board_size):
                p = self.board.get(r, c)
                if p == Player.BLACK:
                    black_score += 1
                elif p == Player.WHITE:
                    white_score += 1
                elif (r, c) not in visited:
                    # Empty spot, check territory
                    territory, owner = self._evaluate_territory(r, c, visited)
                    if owner == Player.BLACK:
                        black_score += len(territory)
                    elif owner == Player.WHITE:
                        white_score += len(territory)
        
        # Komi (6.5 usually, but let's stick to integers or simple logic)
        # Prompt doesn't specify. I'll return the one with higher score.
        if black_score > white_score:
            return Player.BLACK
        elif white_score > black_score:
            return Player.WHITE
        else:
            return None # Draw?

    def _evaluate_territory(self, r, c, visited):
        # BFS to find empty region and neighbors
        region = set()
        stack = [(r, c)]
        visited.add((r, c))
        region.add((r, c))
        
        owners = set() # Players touching this region
        
        while stack:
            curr_r, curr_c = stack.pop()
            
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nr, nc = curr_r + dr, curr_c + dc
                if self.board.is_within_bounds(nr, nc):
                    p = self.board.get(nr, nc)
                    if p is None:
                        if (nr, nc) not in visited:
                            visited.add((nr, nc))
                            region.add((nr, nc))
                            stack.append((nr, nc))
                    else:
                        owners.add(p)
        
        if len(owners) == 1:
            return region, list(owners)[0]
        else:
            return region, None # Neutral

    def check_winner(self):
        return self.winner
