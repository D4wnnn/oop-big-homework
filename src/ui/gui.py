import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import sys
import os

# Ensure src is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.go import GoGame
from game.gomoku import GomokuGame
from game.player import Player
from game.exceptions import GameError, InvalidMoveError
from utils.storage import save_game, load_game

class BoardGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Board Game Platform")
        self.game = None
        self.cell_size = 40
        self.margin = 40
        self.stone_radius = 15
        self.board_size = 15 # Default
        
        # UI Components
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.show_main_menu()

    def show_main_menu(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        title = tk.Label(self.main_frame, text="Board Game Platform", font=("Arial", 24))
        title.pack(pady=50)
        
        btn_frame = tk.Frame(self.main_frame)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="New Go Game", command=lambda: self.start_game_setup('go'), width=20, height=2).pack(pady=10)
        tk.Button(btn_frame, text="New Gomoku Game", command=lambda: self.start_game_setup('gomoku'), width=20, height=2).pack(pady=10)
        tk.Button(btn_frame, text="Load Game", command=self.load_game_dialog, width=20, height=2).pack(pady=10)
        tk.Button(btn_frame, text="Exit", command=self.root.quit, width=20, height=2).pack(pady=10)

    def start_game_setup(self, game_type):
        # Ask for board size
        size = simpledialog.askinteger("Board Size", "Enter board size (8-19):", minvalue=8, maxvalue=19, initialvalue=15 if game_type=='gomoku' else 19)
        if size:
            self.start_game(game_type, size)

    def start_game(self, game_type, size):
        try:
            if game_type == 'go':
                self.game = GoGame(size)
            else:
                self.game = GomokuGame(size)
            self.board_size = size
            self.setup_game_ui()
            self.draw_board()
            self.update_status()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def setup_game_ui(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Top Controls
        control_frame = tk.Frame(self.main_frame)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        tk.Button(control_frame, text="Main Menu", command=self.show_main_menu).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Undo", command=self.undo_move).pack(side=tk.LEFT, padx=5)
        
        if isinstance(self.game, GoGame):
            tk.Button(control_frame, text="Pass", command=self.pass_turn).pack(side=tk.LEFT, padx=5)
            
        tk.Button(control_frame, text="Save", command=self.save_game_dialog).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Restart", command=self.restart_game).pack(side=tk.LEFT, padx=5)

        # Status Bar
        self.status_label = tk.Label(self.main_frame, text="Welcome", font=("Arial", 12), bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        # Canvas
        canvas_width = self.cell_size * (self.board_size - 1) + 2 * self.margin
        canvas_height = self.cell_size * (self.board_size - 1) + 2 * self.margin
        
        self.canvas = tk.Canvas(self.main_frame, width=canvas_width, height=canvas_height, bg="#DEB887") # Wood color
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def draw_board(self):
        self.canvas.delete("all")
        
        # Draw grid
        width = self.cell_size * (self.board_size - 1)
        height = self.cell_size * (self.board_size - 1)
        
        for i in range(self.board_size):
            # Vertical
            x = self.margin + i * self.cell_size
            self.canvas.create_line(x, self.margin, x, self.margin + height)
            # Horizontal
            y = self.margin + i * self.cell_size
            self.canvas.create_line(self.margin, y, self.margin + width, y)
            
        # Draw Hoshi (Stars) for standard sizes
        if self.board_size in [19, 13, 9]:
            self.draw_hoshi()
            
        # Draw Stones
        board = self.game.get_board()
        for r in range(self.board_size):
            for c in range(self.board_size):
                stone = board.get(r, c)
                if stone:
                    self.draw_stone(r, c, stone)
                    
        # Highlight last move? (Optional, but good for UX)

    def draw_hoshi(self):
        # Standard star points
        stars = []
        if self.board_size == 19:
            stars = [(3,3), (3,9), (3,15), (9,3), (9,9), (9,15), (15,3), (15,9), (15,15)]
        elif self.board_size == 13:
            stars = [(3,3), (3,9), (6,6), (9,3), (9,9)]
        elif self.board_size == 9:
            stars = [(2,2), (2,6), (4,4), (6,2), (6,6)]
            
        for r, c in stars:
            x = self.margin + c * self.cell_size
            y = self.margin + r * self.cell_size
            r_dot = 3
            self.canvas.create_oval(x-r_dot, y-r_dot, x+r_dot, y+r_dot, fill="black")

    def draw_stone(self, r, c, player):
        x = self.margin + c * self.cell_size
        y = self.margin + r * self.cell_size
        
        color = "black" if player == Player.BLACK else "white"
        outline = "black" # White stone needs outline
        
        # "Picture display" - simulated with high quality oval rendering
        self.canvas.create_oval(x - self.stone_radius, y - self.stone_radius,
                                x + self.stone_radius, y + self.stone_radius,
                                fill=color, outline=outline)

    def on_canvas_click(self, event):
        if not self.game or self.game.is_game_over():
            return
            
        # Convert x,y to row,col
        # x = margin + col * cell_size -> col = (x - margin) / cell_size
        # We want nearest intersection
        
        col = round((event.x - self.margin) / self.cell_size)
        row = round((event.y - self.margin) / self.cell_size)
        
        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            self.make_move(row, col)

    def make_move(self, row, col):
        try:
            self.game.place_stone(row, col)
            self.draw_board()
            self.check_game_over()
            self.update_status()
        except InvalidMoveError as e:
            messagebox.showwarning("Invalid Move", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def undo_move(self):
        if not self.game: return
        try:
            self.game.undo()
            self.draw_board()
            self.update_status()
        except GameError as e:
            messagebox.showinfo("Undo", str(e))

    def pass_turn(self):
        if not isinstance(self.game, GoGame): return
        try:
            self.game.pass_turn()
            self.update_status()
            self.check_game_over()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def restart_game(self):
        if not self.game: return
        if messagebox.askyesno("Restart", "Are you sure you want to restart?"):
            size = self.game.board_size
            if isinstance(self.game, GoGame):
                self.game = GoGame(size)
            else:
                self.game = GomokuGame(size)
            self.draw_board()
            self.update_status()

    def save_game_dialog(self):
        if not self.game: return
        filename = filedialog.asksaveasfilename(defaultextension=".pkl", filetypes=[("Pickle Files", "*.pkl")])
        if filename:
            success, msg = save_game(self.game, filename)
            if success:
                messagebox.showinfo("Save", msg)
            else:
                messagebox.showerror("Save Error", msg)

    def load_game_dialog(self):
        filename = filedialog.askopenfilename(filetypes=[("Pickle Files", "*.pkl")])
        if filename:
            game, msg = load_game(filename)
            if game:
                self.game = game
                self.board_size = game.board_size
                self.setup_game_ui()
                self.draw_board()
                self.update_status()
                self.check_game_over()
            else:
                messagebox.showerror("Load Error", msg)

    def update_status(self):
        if not self.game: return
        player = self.game.get_current_player()
        text = f"Current Player: {player}"
        
        if isinstance(self.game, GoGame):
            # Show captures
            caps = self.game.captured_stones
            text += f" | Captures: B={caps[Player.BLACK]} W={caps[Player.WHITE]}"
            
        if self.game.is_game_over():
             winner = self.game.check_winner()
             text = f"Game Over! Winner: {winner if winner else 'Draw'}"
             
        self.status_label.config(text=text)

    def check_game_over(self):
        if self.game.is_game_over():
            winner = self.game.check_winner()
            msg = f"Winner: {winner}" if winner else "Draw!"
            messagebox.showinfo("Game Over", msg)

if __name__ == "__main__":
    root = tk.Tk()
    gui = BoardGameGUI(root)
    root.mainloop()
