from abc import ABC, abstractmethod
from typing import Optional, Tuple
from .board import Board
from .player import Player
from .exceptions import InvalidMoveError

class BaseGame(ABC):
    def __init__(self, board_size: int):
        self.board_size = board_size
        self.board = Board(board_size)
        self.current_player = Player.BLACK
        self.history = [] # List of tuples (Board, Player)
        self.game_over = False
        self.winner = None

    def switch_player(self):
        self.current_player = self.current_player.other()

    def save_state(self):
        """Saves the current state to history for undo."""
        self.history.append((self.board.clone(), self.current_player))

    def undo(self):
        """Reverts to the previous state."""
        if not self.history:
            raise InvalidMoveError("No moves to undo.")
        
        prev_board, prev_player = self.history.pop()
        self.board = prev_board
        self.current_player = prev_player
        self.game_over = False
        self.winner = None
        return True

    @abstractmethod
    def place_stone(self, row: int, col: int):
        """Attempts to place a stone. Should raise InvalidMoveError if invalid."""
        pass

    @abstractmethod
    def check_winner(self) -> Optional[Player]:
        """Checks if there is a winner."""
        pass

    def get_board(self):
        return self.board
    
    def get_current_player(self):
        return self.current_player

    def is_game_over(self):
        return self.game_over
