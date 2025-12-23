import random
import sqlite3

class WhoAmI:
    id = "who-am-i"
    title = "Who am I?"
    duration = 20*60
    max_points = 1200
    team_distribution = "Individual"
    description = """Game Description:
    
Every player will get assigned a person or character (real/fake/alive/dead all possible).

The goal of the game is for everyone to guess their character using only yes/no questions. However, the questions won't be asked in the whole group. Instead, you will split into pairs of 2 and each ask 2 yes/no questions, which the other will answer.

You will be able to guess at any moment. If you want to guess a name, either first name, surname or first name + surname will be accepted.

If there is normally a "-" in the name, put a space instead.

If there is normally an accent on the letter, put the plain letter instead: é -> e.

Make sure to spell it correctly! Look it up if needed.

When answering a question it's okay to Google it only if you reeeaaally have no idea, otherwise take your best guess.


Scoring:

The number of points you earn for the team is dependant on the number of questions you have asked.

If you answer correctly within 4 questions, you will earn the full 300 points for the group. Every extra question taken will deduct 15 points.
For every incorrect guess 25 points will be deducted.
Everyone will also get an easy secret task worth 100 points and a hard secret task worth 250 points."""
    
    # worth 100 points
    easy_tasks = [
        "Answer \"Yes\" 3 times in a row",
        "Answer \"No\" 3 times in a row",
        "Answer two questions with \"Yes and No\"",
        "Ask the same question three times",
        "Answer a question with a confident \"Yes\", then switch to a \"No\" after 5 seconds",
        "Answer a question with a confident \"No\", then switch to a \"Yes\" after 5 seconds",
        "Before asking a question, do a squat without the other person saying anything about it",
        "Before asking a question, do a full 360 degree turn without the other person saying anything about it",
        "Before asking a question, do a max height jump without the other person saying anything about it",
        "Before asking a question, touch the other persons shoulder without the other person saying anything about it",
        "Get 3 high fives in total during the game",
        "Have someone say your name 4 times during the game",
        "Make someone laugh",
        "Ask a question to which someone does not respond with \"Yes\" or \"No\"",
        "Solve your character in the least amount of questions",
        "Ask a question that makes the other person Google an answer",
        "Have someone ask the same question as you just asked",
    ]
    
    # worth 250 points
    hard_tasks = [
        "Answer \"Yes\" 5 times in a row",
        "Answer \"No\" 5 times in a row",
        "Ask the same question to the same person three times",
        "Answer two questions in a row, to the same person, with \"Yes and No\"",
        "Answer a question with a confident \"Yes\", then switch to a \"No\" in your next meetup with that person",
        "Answer a question with a confident \"No\", then switch to a \"Yes\" in your next meetup with that person",
        "Three times before asking a question, do a squat without the other person saying anything about it",
        "Three times before asking a question, do a full 360 degree turn without the other person saying anything about it",
        "Three times before asking a question, do a max height jump without the other person saying anything about it",
        "Three times before asking a question, touch the other persons shoulder without the other person saying anything about it",
        "Get 7 high fives in total during the game",
        "Have someone say your name 8 times during the game",
        "Make three different people laugh",
        "Ask three questions to which someone does not respond with \"Yes\" or \"No\"",
        "Solve your character with 2 less questions asked than anyone else",
        "Ask three questions that make the other person Google an answer",
        "Have two different people ask the same question that you just asked",
    ]

    # --- SETUP ---
    def setup_db(self, cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS whoami_state (
                player_id INTEGER PRIMARY KEY,
                character TEXT,
                easy_task TEXT,
                hard_task TEXT,
                easy_complete BOOLEAN DEFAULT 0,
                hard_complete BOOLEAN DEFAULT 0,
                questions_asked INTEGER DEFAULT 0,
                wrong_guesses INTEGER DEFAULT 0,
                is_solved BOOLEAN DEFAULT 0,
                points_earned INTEGER DEFAULT 0
            )
        """)

    def generate_secret_state(self, cursor):
        cursor.execute("DELETE FROM whoami_state")
        
        # Cursor comes from main, which already has Row factory set
        players = cursor.execute("SELECT id FROM players").fetchall()
        
        random.shuffle(self.characters)
        mole_intel = {}

        for i, p in enumerate(players):
            char = self.characters[i % len(self.characters)]
            easy = random.choice(self.easy_tasks)
            hard = random.choice(self.hard_tasks)
            
            cursor.execute("""
                INSERT INTO whoami_state (player_id, character, easy_task, hard_task) 
                VALUES (?, ?, ?, ?)
            """, (p['id'], char, easy, hard))
            
            mole_intel[p['id']] = {"char": char, "easy": easy, "hard": hard}

        return mole_intel

    # --- VIEW ---
    def get_player_view(self, cursor, player_id, is_mole, dynamic_secret):
        my_state = cursor.execute("SELECT * FROM whoami_state WHERE player_id = ?", (player_id,)).fetchone()
        
        view = {
            "game_id": self.id,
            "tasks": [
                {"desc": my_state['easy_task'], "done": bool(my_state['easy_complete']), "type": "easy"},
                {"desc": my_state['hard_task'], "done": bool(my_state['hard_complete']), "type": "hard"}
            ],
            "stats": {
                "questions": my_state['questions_asked'],
                "strikes": my_state['wrong_guesses'],
                "solved": bool(my_state['is_solved']),
                "points": my_state['points_earned']
            }
        }

        others_rows = cursor.execute("""
            SELECT p.name, w.character 
            FROM whoami_state w 
            JOIN players p ON w.player_id = p.id 
            WHERE w.player_id != ?
        """, (player_id,)).fetchall()
        
        view['others'] = [{"name": r['name'], "char": r['character']} for r in others_rows]

        if is_mole:
            # MOLE SPECIFIC: Show their own character too!
            view['role_text'] = f"Role: MOLE.\nYour Character: {my_state['character'].upper()}. Pretend that you don't know your character and earn points by making sure that you and the other players don't guess the character too quickly."
        else:
            view['role_text'] = "Role: INNOCENT. Guess your character to earn points!"

        return view

    # --- INTERACTION ---
    def handle_action(self, cursor, player_id, action, payload):
        if action == "add_question":
            cursor.execute("UPDATE whoami_state SET questions_asked = questions_asked + 1 WHERE player_id = ?", (player_id,))
            return {"status": "updated"}
        
        if action == "toggle_task":
            # Payload: { "task_index": 0 } (0 for easy, 1 for hard)
            idx = payload.get("task_index")
            col = "easy_complete" if idx == 0 else "hard_complete"
            
            # Toggle logic
            current = cursor.execute(f"SELECT {col} FROM whoami_state WHERE player_id = ?", (player_id,)).fetchone()[0]
            new_val = 0 if current else 1
            
            cursor.execute(f"UPDATE whoami_state SET {col} = ? WHERE player_id = ?", (new_val, player_id))
            return {"status": "updated"}

        if action == "guess":
            guess = payload.get("guess", "").lower().strip()
            row = cursor.execute("SELECT character, questions_asked, wrong_guesses FROM whoami_state WHERE player_id = ?", (player_id,)).fetchone()
            target = row['character']
            
            if guess in target and len(guess) > 2:
                # Calculate Pot Points (Not individual points yet, those happen at end)
                qs = row['questions_asked']
                wrongs = row['wrong_guesses']
                base = 300
                q_penalty = max(0, (qs - 4) * 15)
                w_penalty = wrongs * 25
                score = max(0, base - q_penalty - w_penalty)
                
                cursor.execute("UPDATE whoami_state SET is_solved = 1, points_earned = ? WHERE player_id = ?", (score, player_id))
                return {"result": "correct", "points": score, "real_name": target}
            else:
                cursor.execute("UPDATE whoami_state SET wrong_guesses = wrong_guesses + 1 WHERE player_id = ?", (player_id,))
                return {"result": "incorrect"}

        return {"error": "Unknown action"}

    # --- SCORING ---
    def calculate_scores(self, cursor):
        """
        1. Sum up all character guessing points -> Give to Innocents.
        2. Give (Max - Sum) -> To Mole.
        3. Add individual task points to specific players.
        """
        rows = cursor.execute("SELECT * FROM whoami_state").fetchall()
        num_players = len(rows)
        
        # 1. Calculate The Pot
        total_pot_earned = 0
        total_pot_possible = num_players * 300
        
        for r in rows:
            if r['is_solved']:
                total_pot_earned += r['points_earned']
            else:
                # Unsolved penalty still applies to the pot contribution
                penalty = r['wrong_guesses'] * 25
                total_pot_earned -= penalty
        
        # Ensure pot isn't negative
        total_pot_earned = max(0, total_pot_earned)
        mole_pot_earned = max(0, total_pot_possible - total_pot_earned)

        # 2. Distribute Pot & Task Points
        players = cursor.execute("SELECT id, is_mole FROM players").fetchall()
        
        for p in players:
            pid = p['id']
            # Find specific task state
            state = next((r for r in rows if r['player_id'] == pid), None)
            
            round_score = 0
            
            # A. Pot Score
            if p['is_mole']:
                round_score += mole_pot_earned
            else:
                round_score += total_pot_earned
            
            # B. Task Score (Individual)
            if state['easy_complete']:
                round_score += 100
            if state['hard_complete']:
                round_score += 250
            
            # Update
            cursor.execute("UPDATE players SET score = score + ? WHERE id = ?", (round_score, pid))
            
            
    characters = [
        " barack obama ", " donald trump ", " mark rutte ", " willem alexander ", 
        " angela merkel ", " elon musk ", " queen elizabeth ", " putin ", " kim jong un ",
        " leonardo dicaprio ", " adolf hitler ", " napoleon bonaparte ",
        " pewdiepie ", " kim kardashian ", " kanye west ",
        " justin bieber ", " taylor swift ", " billie eilish ", " beyonce ",
        " gordon ramsay ", " snoop dogg ", " enzo knol ", " mrbeast ",
        " hermione granger ", " harry potter ", " darth vader ", " shrek ",
        " spiderman ", " batman ", " joker ", " dracula ", " frankenstein ", 
        " walter white ", " captain jack sparrow ", " james bond ", " sherlock holmes ",
        " spongebob squarepants ", " donald duck ", " mickey mouse ",
        " snow white ", " cinderella ", " steve ( minecraft ) ",
        " iron man ", " thanos ", " godzilla ", " king kong ", " mufasa ( lion king )",
        " max verstappen ", " lionel messi ", " cristiano ronaldo ",
        " michael jackson ", " elvis presley ", " marilyn monroe ",
        " vincent van gogh ", " anne frank ", " albert einstein ", " isaac newton "
        " jesus ", " satan ", " santa claus ", " zwarte piet ", 
        " julius caesar ", " cleopatra ", " sinterklaas ", " easter bunny ",
        " god ", " zeus ", " poseidon ", " mario ", " luigi ", " princess peach ",
        " yoshi ", " donkey kong ", " sonic the hedgehog ", " waluigi "
        " pikachu ", " ash ketchum ", " charizard ", " bulbasaur ",
        " squirtle ", " blastoise ", " eevee ", " mewtwo ", 
        " barbarian king ", " archer queen ", " P.E.K.K.A ( pekka ) ",
        " minecraft steve ", " aang ", " katara ", " sokka ", " zuko ",
        " azula ", " toph ", " uncle iroh ", " winnie the pooh ", 
        " bob the builder ", " dora the explorer ", " nijntje ( miffy )",
        " neo ( the matrix )", " buzz lightyear ", " lightning mcqueen ",
        " william shakespear ", " medusa ", " pinocchio ", " yoda ",
        " barbie ", " tarzan ", " genghis khan ", " cupid ", " robin hood ",
        " marco polo ", " gandalf ", " frodo ", " legolas ", " kermit the frog ",
        " puss in boots ", " hercules ", " jackie chan ", " thor ", " loki ",
        " willy wonka ", " peter pan ", " homer simpson ", " lara croft ",
        " lars vellinga ", " abedin heij ", " arne arends ", " fabian verheul ",
    ]