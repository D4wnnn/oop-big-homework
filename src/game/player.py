from enum import Enum

class Player(Enum):
    BLACK = 1
    WHITE = 2

    def other(self):
        return Player.WHITE if self == Player.BLACK else Player.BLACK

    def __str__(self):
        return "Black" if self == Player.BLACK else "White"

    def symbol(self):
        return "X" if self == Player.BLACK else "O"
