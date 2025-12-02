class GameError(Exception):
    """Base class for game exceptions."""
    pass

class InvalidMoveError(GameError):
    """Raised when a move is invalid."""
    pass

class InvalidBoardSizeError(GameError):
    """Raised when board size is invalid."""
    pass
