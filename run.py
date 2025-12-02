import sys
import os

# Add src to path
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.append(src_path)

from ui.cli import CLI

if __name__ == "__main__":
    cli = CLI()
    cli.start()
