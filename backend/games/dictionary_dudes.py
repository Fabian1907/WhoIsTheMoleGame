import random

class DictionaryDudes:
    id = "dictionary-dudes"
    title = "Dictionary Dudes"
    duration = 10 * 60 
    max_points = 1600
    team_distribution = "2 solos and the rest"
    description = """The two solo players will be able to see a list of 80 words, numbered 1-80, that they need to communicate to the team.
    
One of them will be only allowed to communicate in drawing (letters, numbers and symbols not allowed).
The other will only be allowed to communicate in short written descriptions of 5 words or less.

The Guessing team is not allowed to say the description out loud or describe the drawing, so that the solos cannot know what the other person is doing.

The drawings or descriptions will be given in notes and should have the number of the word it is about in the top left.
 
Every word guessed correctly (for the correct number) is worth 20 points.
There are no hidden tasks in this game."""
    
    # 100+ Common Words
    words = [
        "table", "time", "water", "person", "year", "way", "day", "man", "world", "life",
        "hand", "part", "child", "eye", "woman", "place", "work", "week", "case", "point",
        "government", "company", "number", "group", "problem", "fact", "apple", "banana", "chair", "dog",
        "cat", "sun", "moon", "star", "river", "mountain", "ocean", "forest", "tree", "flower",
        "car", "train", "plane", "ship", "bicycle", "house", "building", "city", "road", "bridge",
        "computer", "phone", "book", "pen", "paper", "music", "movie", "art", "science", "history",
        "love", "friend", "family", "money", "food", "game", "team", "school", "student", "teacher",
        "doctor", "hospital", "police", "fire", "army", "king", "queen", "president", "country", "flag",
        "red", "blue", "green", "yellow", "white", "black", "big", "small", "good", "bad",
        "hot", "cold", "fast", "slow", "happy", "sad", "new", "old", "rich", "poor",
        "run", "walk", "eat", "drink", "sleep", "dream", "think", "speak", "write", "read",
        "umbrella", "key", "clock", "mirror", "hammer", "window", "door", "cloud", "rain", "snow",
        "pizza", "bread", "cake", "milk", "coffee", "shoe", "hat", "glasses", "ring", "gift",
        "map", "camera", "battery", "light", "candle", "ladder", "pocket", "suitcase", "pillow", "blanket",
        "dance", "climb", "fight", "shout", "laugh", "cry", "win", "lose", "hide", "seek",
        "space", "gravity", "future", "past", "justice", "peace", "danger", "secret", "luck", "voice",
        "pilot", "chef", "astronaut", "farmer", "lion", "elephant", "snake", "shark", "butterfly", "owl",
        "volcano", "desert", "island", "cave", "beach", "lightning", "rainbow", "planet", "galaxy", "shadow",
        "basket", "bucket", "compass", "magnet", "needle", "soap", "towel", "brush", "crown", "mask",
        "glove", "watch", "belt", "honey", "cheese", "egg", "soup", "salt", "spider", "monkey",
        "turtle", "bee", "soldier", "nurse", "judge", "clown", "pirate", "ghost", "swim", "jump",
        "cook", "clean", "memory", "energy", "power", "truth", "magic", "health", "safety", "noise",
        "silence", "rocket", "submarine", "truck", "helicopter", "ticket", "tent", "tunnel", "guitar", "piano",
        "diamond", "gold", "silver", "iron", "bottle", "spoon", "knife", "fork", "plate", "bowl",
        "button", "string", "anchor", "balloon", "castle", "desert", "jungle", "swamp", "bridge", "statue",
        "lemon", "grape", "orange", "onion", "carrot", "potato", "bread", "butter", "sugar", "pepper",
        "dragon", "unicorn", "robot", "alien", "monster", "hero", "villain", "thief", "wizard", "knight",
        "anchor", "balloon", "battery", "beast", "bell", "bench", "bone", "bottle", "bowl", "box",
        "brain", "brick", "broom", "bubble", "button", "cactus", "castle", "chain", "chalk", "chess",
        "circus", "claw", "coach", "coin", "comb", "cookie", "copper", "cotton", "curtain", "desk",
        "diamond", "dice", "dragon", "drum", "duck", "dust", "eagle", "earth", "engine", "feather",
        "fence", "flame", "fork", "fountain", "frame", "frog", "fuel", "garden", "gate", "giant",
        "glass", "gold", "grape", "guitar", "heart", "helmet", "hero", "hook", "ice", "iron",
        "jacket", "jar", "jelly", "jewel", "jungle", "knight", "knot", "lamp", "leaf", "lemon",
        "letter", "library", "lizard", "lock", "loop", "lunch", "magic", "magnet", "marble", "medal",
        "metal", "microscope", "monster", "mouse", "nail", "necklace", "needle", "nest", "net", "night",
        "nose", "ocean", "oil", "onion", "orange", "paint", "palace", "pan", "pants", "parrot"
    ]

    def setup_db(self, cursor):
        pass # No state tracking needed

    def generate_secret_state(self, cursor):
        # Pick 70 unique words
        words_no_dup = list(set(self.words))
        selected = random.sample(words_no_dup, 80)
        # Store as simple list
        return {"words": selected}

    def get_mole_text(self, dynamic_secret):
        # Mole gets a sneak peek
        txt = "SNEAK PEEK (Word List):\n"
        for i, w in enumerate(dynamic_secret['words']):
            txt += f"{i+1}. {w}\n"
        return txt

    def get_innocent_text(self, dynamic_secret):
        return "Decide who will be the Drawing/Writing solos. The rest are guessers!"

    # --- VIEW ---
    def get_player_view(self, cursor, player_id, is_mole, dynamic_secret):
        # Everyone gets the list, but it's hidden on the frontend
        view = {
            "game_id": self.id,
            "word_list": dynamic_secret['words']
        }
        
        if is_mole:
            view['role_text'] = "Role: MOLE.\nFind a way to subtly influence the team into guessing the wrong words!"
        else:
            view['role_text'] = "Role: INNOCENT.\nCoordinate and guess!"
            
        return view

    # --- INTERACTION ---
    def handle_action(self, cursor, player_id, action, payload):
        return {"error": "No actions supported"}

    # --- SCORING ---
    def calculate_scores(self, cursor):
        # Manual input handled by main.py logic (submit_score)
        pass