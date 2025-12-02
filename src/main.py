import sys
import os

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from ui.cli import CLI

if __name__ == "__main__":
    cli = CLI()
    cli.start()
