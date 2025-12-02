import pickle
import os

def save_game(game_instance, filename):
    try:
        with open(filename, 'wb') as f:
            pickle.dump(game_instance, f)
        return True, "Game saved successfully."
    except Exception as e:
        return False, f"Failed to save game: {str(e)}"

def load_game(filename):
    if not os.path.exists(filename):
        return None, "File not found."
    try:
        with open(filename, 'rb') as f:
            game = pickle.load(f)
        return game, "Game loaded successfully."
    except Exception as e:
        return None, f"Failed to load game: {str(e)}"
