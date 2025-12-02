import sys
import os
import tkinter as tk

# Add src to path
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.append(src_path)

from ui.gui import BoardGameGUI

if __name__ == "__main__":
    root = tk.Tk()
    # Set initial size
    root.geometry("800x850")
    gui = BoardGameGUI(root)
    root.mainloop()
