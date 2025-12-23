from games.who_am_I import WhoAmI
from games.chess_challenges import ChessChallenges
from games.dictionary_dudes import DictionaryDudes
from games.risky_business import RiskyBusiness

# List of available game classes
GAME_LIST = [
    WhoAmI(),
    ChessChallenges(),
    DictionaryDudes(),
    RiskyBusiness(),
    # Add new games here: WordGame(), QuizGame(), etc.
]

# Helper to find a game by index
def get_game_by_index(idx):
    if 0 <= idx < len(GAME_LIST):
        return GAME_LIST[idx]
    return None