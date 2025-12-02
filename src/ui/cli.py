import sys
import os

# Add the parent directory to path so we can import modules if running directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.go import GoGame
from game.gomoku import GomokuGame
from game.player import Player
from game.exceptions import GameError
from utils.storage import save_game, load_game

class CLI:
    def __init__(self):
        self.game = None
        self.running = True
        self.show_hints = True

    def start(self):
        print("Welcome to the Board Game Platform!")
        print("Type 'help' for commands.")
        while self.running:
            try:
                line = input(">>> ").strip()
                if not line:
                    continue
                self.process_command(line)
            except KeyboardInterrupt:
                print("\nExiting...")
                self.running = False
            except Exception as e:
                print(f"Error: {e}")

    def process_command(self, line):
        parts = line.split()
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd == 'help':
            self.show_help()
        elif cmd == 'exit' or cmd == 'quit':
            self.running = False
        elif cmd == 'start':
            self.cmd_start(args)
        elif cmd == 'restart':
            self.cmd_restart()
        elif cmd == 'place':
            self.cmd_place(args)
        elif cmd == 'pass':
            self.cmd_pass()
        elif cmd == 'undo':
            self.cmd_undo()
        elif cmd == 'resign':
            self.cmd_resign()
        elif cmd == 'save':
            self.cmd_save(args)
        elif cmd == 'load':
            self.cmd_load(args)
        elif cmd == 'hints':
            self.cmd_hints(args)
        else:
            print("Unknown command. Type 'help' for list.")

    def show_help(self):
        print("Commands:")
        print("  start <go|gomoku> <size>  : Start a new game (size 8-19)")
        print("  restart                   : Restart current game")
        print("  place <row> <col>         : Place stone (e.g., 'place 3 4')")
        print("  pass                      : Pass turn (Go only)")
        print("  undo                      : Undo last move")
        print("  resign                    : Resign the game")
        print("  save <filename>           : Save game to file")
        print("  load <filename>           : Load game from file")
        print("  hints <on|off>            : Show/Hide hints")
        print("  exit                      : Exit program")

    def cmd_start(self, args):
        if len(args) != 2:
            print("Usage: start <go|gomoku> <size>")
            return
        
        gtype = args[0].lower()
        try:
            size = int(args[1])
        except ValueError:
            print("Size must be an integer.")
            return

        try:
            if gtype == 'go':
                self.game = GoGame(size)
            elif gtype == 'gomoku':
                self.game = GomokuGame(size)
            else:
                print("Unknown game type. Choose 'go' or 'gomoku'.")
                return
            print(f"Started {gtype.capitalize()} game on {size}x{size} board.")
            self.print_board()
        except GameError as e:
            print(f"Error starting game: {e}")

    def cmd_restart(self):
        if not self.game:
            print("No active game.")
            return
        # Re-initialize with same params
        size = self.game.board_size
        if isinstance(self.game, GoGame):
            self.game = GoGame(size)
        else:
            self.game = GomokuGame(size)
        print("Game restarted.")
        self.print_board()

    def cmd_place(self, args):
        if not self.game:
            print("No active game. Use 'start' first.")
            return
        if len(args) != 2:
            print("Usage: place <row> <col>")
            return
        
        try:
            # User input is likely 1-based
            r = int(args[0]) - 1
            c = int(args[1]) - 1
            
            self.game.place_stone(r, c)
            self.print_board()
            self.check_game_over()
            
        except ValueError:
            print("Coordinates must be integers.")
        except GameError as e:
            print(f"Invalid move: {e}")

    def cmd_pass(self):
        if not self.game:
            print("No active game.")
            return
        
        if isinstance(self.game, GoGame):
            try:
                self.game.pass_turn()
                print(f"{self.game.get_current_player().other()} passed.")
                self.check_game_over()
                # Only print board if game not over to show 'passed' state?
                # Actually pass doesn't change board, but maybe we should show whose turn it is.
                if not self.game.is_game_over():
                    print(f"Current Player: {self.game.get_current_player()}")
            except GameError as e:
                print(f"Error: {e}")
        else:
            print("Pass is only available in Go.")

    def cmd_undo(self):
        if not self.game:
            print("No active game.")
            return
        try:
            self.game.undo()
            print("Undid last move.")
            self.print_board()
        except GameError as e:
            print(f"Cannot undo: {e}")

    def cmd_resign(self):
        if not self.game:
            print("No active game.")
            return
        
        winner = self.game.get_current_player().other()
        print(f"{self.game.get_current_player()} resigns. {winner} wins!")
        self.game.game_over = True
        self.game.winner = winner

    def cmd_save(self, args):
        if not self.game:
            print("No active game.")
            return
        if len(args) != 1:
            print("Usage: save <filename>")
            return
        
        success, msg = save_game(self.game, args[0])
        print(msg)

    def cmd_load(self, args):
        if len(args) != 1:
            print("Usage: load <filename>")
            return
        
        game, msg = load_game(args[0])
        if game:
            self.game = game
            print(msg)
            self.print_board()
            self.check_game_over()
        else:
            print(msg)

    def cmd_hints(self, args):
        if len(args) != 1:
            print("Usage: hints <on|off>")
            return
        mode = args[0].lower()
        if mode == 'on':
            self.show_hints = True
            print("Hints enabled.")
        elif mode == 'off':
            self.show_hints = False
            print("Hints disabled.")
        else:
            print("Invalid option.")

    def check_game_over(self):
        if self.game.is_game_over():
            w = self.game.check_winner()
            if w:
                print(f"Game Over! Winner: {w}")
            else:
                print("Game Over! Draw.")

    def print_board(self):
        if not self.game:
            return
        
        b = self.game.get_board()
        size = b.size
        
        # Column headers
        header = "   " + " ".join([f"{i+1:<2}" for i in range(size)])
        print(header)
        
        for r in range(size):
            row_str = f"{r+1:<2} "
            for c in range(size):
                p = b.get(r, c)
                if p == Player.BLACK:
                    symbol = "X " # or ●
                elif p == Player.WHITE:
                    symbol = "O " # or ○
                else:
                    # Grid intersection style could be fancy, but simple . is clearer for CLI
                    symbol = ". " 
                row_str += symbol
            print(row_str)
        
        if self.show_hints and not self.game.is_game_over():
            print(f"Turn: {self.game.get_current_player()} ({self.game.get_current_player().symbol().strip()})")
            if isinstance(self.game, GoGame):
                print(f"Captures - Black: {self.game.captured_stones[Player.BLACK]}, White: {self.game.captured_stones[Player.WHITE]}")

if __name__ == "__main__":
    CLI().start()
