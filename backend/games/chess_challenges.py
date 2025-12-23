import random
import json

class ChessChallenges:
    id = "chess-challenges"
    title = "Chess Challenges"
    duration = 20*60 
    max_points = "Variable"
    team_distribution = "2 equal teams"
    description = """In this game you will play a chess game in teams of 2, alternating moves.
The goal of the game is to complete as many hidden challenges as possible. Some challenges will earn points for the group, and some challenges will earn individual points

You will be able to play either 20 minutes, or each player 20 moves, or until one of the kings is slain, whichever comes first.

You may not talk about the game at all. Talking about anything related to a challenge will mean it is immediately failed.

There is a big bonus of 400 points for the team that wins the chess game (by taking the opponent's king).

Everyone will get 3 team challenges and 2 individual challenges, the points gained from them will be shown. 
    """
    
    # (challenge, points earned)
    challenges = {
        "Promote a pawn": 100,
        "Promote a pawn to a rook": 150,
        "Promote a pawn to a bishop": 200,
        "Promote a pawn to a knight": 200,
        "Promote two pawns": 250,
        "Win a piece using a fork": 80,
        "Win a piece using a fork with a knight": 120,
        "Win a piece using a fork with a pawn": 120,
        "Win a piece using a fork with a bishop": 150,
        "Win a piece using a fork with a rook": 180,
        "Win a rook using a fork": 120,
        "Win a bishop using a fork": 150,
        "Win a knight using a fork": 150,
        "Win a queen using a fork": 200,
        "Win a piece using a skewer": 100,
        "Win a piece using a skewer with a bishop": 120,
        "Win a piece using a skewer with a rook": 120,
        "Win a rook using a skewer": 140,
        "Win a queen using a skewer": 180,
        "Do a short castle": 50,
        "Do a long castle": 80,
        "Take a pawn using en passant": 130,
        "Take a bishop with a pawn": 90,
        "Take a bishop with a bishop": 70,
        "Take a bishop with a queen": 100,
        "Take a bishop with a king": 200,
        "Take a knight with a knight": 70,
        "Take a knight with a rook": 100,
        "Take a knight with a bishop": 60,
        "Take a knight with a king": 200,
        "Take a queen with a pawn": 150,
        "Take a queen with a knight": 100,
        "Take a queen with a rook": 100,
        "Take a queen with a king": 300,
        "Take a king with a pawn": 300,
        "Take 2 pieces with the same piece": 100,
        "Take 3 pieces with the same piece": 140,
        "Take 4 pieces with the same piece": 180,
        "Take 3 pieces with the same pawn": 250,
        "Do not take any pieces for 5 consecutive turns": 50,
        "Do not take any pieces for 10 consecutive turns": 200,
        "Do not take any pieces for the entire game": 300,
        "Move the same piece for 3 consecutive turns": 80,
        "Move the same piece for 4 consecutive turns": 120,
        "Move the same piece for 5 consecutive turns": 160,
        "Move the same pawn for 4 consecutive turns": 180,
        "Move the same knight for 5 consecutive turns": 180,
        "Move a pawn for 5 consecutive turns": 110,
        "Move a pawn for 7 consecutive turns": 180,
        "Move a pawn for 10 consecutive turns": 220,
        "Move the king for 3 consecutive turns": 100,
        "Move the king for 4 consecutive turns": 140,
        "Move the king for 5 consecutive turns": 180,
        "Have a piece taken after your turn 3 times": 50,
        "Have a piece taken after your turn 7 times": 100,
        "Have a piece taken after your turn 11 times": 200,
        "Have all your untaken pawns on black squares": 60,
        "Have all your untaken pawns on white squares": 60,
        "Have 6 pawns on black squares": 80,
        "Have 8 pawns on black squares": 180,
        "Have 6 pawns on white squares": 80,
        "Have 8 pawns on white squares": 180,
        "Move your king into the line of sight of an enemy piece": 200,
        "Sacrifice a rook for a bishop": 80,
        "Sacrifice a rook for a knight": 80,
        "Sacrifice a queen for a bishop": 140,
        "Sacrifice a queen for a kinght": 140,
        "Sacrifice a queen for a rook": 120,
        "Have 3 pawns in the same column": 180,
        "Have 4 pawns in the same row (other than the starting row)": 120,
        "Have 5 pawns in the same row (other than the starting row)": 150,
        "Have 6 pawns in the same row (other than the starting row)": 200,
        "Have 8 pawns in the same row (other than the starting row)": 300,
        "Move a knight to one of the corners of the board": 150,
        "Get the same rook to all the corners of the board once": 150,
        "Take 2 knights": 120,
        "Take 2 bishops": 120,
        "Take 2 rooks": 120,
        "Take 2 queens": 350,
        "Take 6 pawns": 180,
        "Take 4 pawns": 120,
        "Do 2 double pawn moves (the 2 step from the start)": 50,
        "Do 4 double pawn moves (the 2 step from the start)": 100,
        "Do 6 double pawn moves (the 2 step from the start)": 160,
        "Do 8 double pawn moves (the 2 step from the start)": 280,
        "End the game in a stalemate": 500,
    }
    
    # --- SETUP ---
    def setup_db(self, cursor):
        # We store challenges as JSON strings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chess_state (
                player_id INTEGER PRIMARY KEY,
                group_tasks TEXT,      -- JSON list of {desc, points}
                indiv_tasks TEXT,      -- JSON list of {desc, points}
                group_complete TEXT,   -- JSON list of booleans
                indiv_complete TEXT,   -- JSON list of booleans
                moves_made INTEGER DEFAULT 0,
                game_won BOOLEAN DEFAULT 0
            )
        """)

    # --- LOGIC ---
    def generate_secret_state(self, cursor):
        cursor.execute("DELETE FROM chess_state")
        players = cursor.execute("SELECT id, name FROM players").fetchall()
        num_players = len(players)
        
        # 1. Resource Calculation
        # We need 3 Group + 2 Indiv per player.
        # Total needed = 5 * NumPlayers.
        total_needed = 5 * num_players
        keys = list(self.challenges.keys())
        
        if len(keys) < total_needed:
            # Fallback if we somehow run out of unique challenges (unlikely with ~70 challenges)
            random.shuffle(keys)
            selected_keys = (keys * 2)[:total_needed]
        else:
            selected_keys = random.sample(keys, total_needed)
            
        mole_intel_data = {}

        # 2. Distribution
        # Slice the massive list of keys into chunks for each player
        for i, p in enumerate(players):
            start = i * 5
            # First 3 are Group, Next 2 are Individual
            p_group_keys = selected_keys[start : start+3]
            p_indiv_keys = selected_keys[start+3 : start+5]
            
            group_tasks_data = [{"desc": k, "points": self.challenges[k]} for k in p_group_keys]
            indiv_tasks_data = [{"desc": k, "points": self.challenges[k]} for k in p_indiv_keys]
            
            group_complete_init = [False] * 3 
            indiv_complete_init = [False] * 2

            cursor.execute("""
                INSERT INTO chess_state 
                (player_id, group_tasks, indiv_tasks, group_complete, indiv_complete)
                VALUES (?, ?, ?, ?, ?)
            """, (
                p['id'], 
                json.dumps(group_tasks_data), 
                json.dumps(indiv_tasks_data), 
                json.dumps(group_complete_init), 
                json.dumps(indiv_complete_init)
            ))
            
            # Store data for the Mole Explanation Screen
            mole_intel_data[p['id']] = {
                "name": p['name'],
                "group": p_group_keys
            }

        return mole_intel_data

    # --- TEXT GENERATORS ---
    def get_mole_text(self, dynamic_secret):
        # This shows in the EXPLANATION screen for the Mole
        txt = "SECRET INTEL (Who has which Group Task):\n"
        for pid, data in dynamic_secret.items():
            txt += f"\n👤 {data['name']}:\n"
            for task in data['group']:
                txt += f"- {task}\n"
        return txt

    def get_innocent_text(self, dynamic_secret):
        return "You will be assigned unique Group and Individual challenges.\nYou will also see some challenges belonging to others, but you won't know who owns them."

    # --- VIEW ---
    def get_player_view(self, cursor, player_id, is_mole, dynamic_secret):
        row = cursor.execute("SELECT * FROM chess_state WHERE player_id = ?", (player_id,)).fetchone()
        
        # 1. My Tasks
        g_tasks = json.loads(row['group_tasks'])
        i_tasks = json.loads(row['indiv_tasks'])
        g_done = json.loads(row['group_complete'])
        i_done = json.loads(row['indiv_complete'])
        
        group_view = []
        for idx, t in enumerate(g_tasks):
            group_view.append({**t, "done": g_done[idx], "idx": idx})
            
        indiv_view = []
        for idx, t in enumerate(i_tasks):
            indiv_view.append({**t, "done": i_done[idx], "idx": idx})

        # 2. Anonymous Intel (See 3 tasks from others, BUT HIDE STATUS)
        others_rows = cursor.execute("SELECT group_tasks FROM chess_state WHERE player_id != ?", (player_id,)).fetchall()
        
        all_other_tasks = []
        for r in others_rows:
            tasks = json.loads(r['group_tasks'])
            for k in range(len(tasks)):
                all_other_tasks.append({
                    "desc": tasks[k]['desc'],
                    "points": tasks[k]['points']
                    # REMOVED "done" status to keep it a mystery
                })
        
        all_other_tasks.sort(key=lambda x: x['desc'])
        
        seen_tasks = []
        if all_other_tasks:
            total = len(all_other_tasks)
            start_idx = (player_id * 3) % total
            for i in range(3):
                idx = (start_idx + i) % total
                seen_tasks.append(all_other_tasks[idx])

        view = {
            "game_id": self.id,
            "group_tasks": group_view,
            "indiv_tasks": indiv_view,
            "anonymous_tasks": seen_tasks,
            "stats": {
                "moves": row['moves_made'],
                "game_won": bool(row['game_won'])
            }
        }
        
        if is_mole:
            view['role_text'] = "Role: MOLE.\nSabotage the group tasks. Complete your individual tasks."
        else:
            view['role_text'] = "Role: INNOCENT.\nComplete tasks to earn points!"
            
        return view

    # --- INTERACTION ---
    def handle_action(self, cursor, player_id, action, payload):
        if action == "add_move":
            cursor.execute("UPDATE chess_state SET moves_made = moves_made + 1 WHERE player_id = ?", (player_id,))
            return {"status": "updated"}

        if action == "toggle_win":
            curr = cursor.execute("SELECT game_won FROM chess_state WHERE player_id = ?", (player_id,)).fetchone()[0]
            new_val = 0 if curr else 1
            cursor.execute("UPDATE chess_state SET game_won = ? WHERE player_id = ?", (new_val, player_id))
            return {"status": "updated"}
        
        if action == "toggle_group":
            # LOCAL ONLY UPDATE
            idx = payload.get("index")
            row = cursor.execute("SELECT group_complete FROM chess_state WHERE player_id = ?", (player_id,)).fetchone()
            g_list = json.loads(row['group_complete'])
            g_list[idx] = not g_list[idx]
            cursor.execute("UPDATE chess_state SET group_complete = ? WHERE player_id = ?", 
                           (json.dumps(g_list), player_id))
            return {"status": "updated"}

        if action == "toggle_indiv":
            idx = payload.get("index")
            row = cursor.execute("SELECT indiv_complete FROM chess_state WHERE player_id = ?", (player_id,)).fetchone()
            i_list = json.loads(row['indiv_complete'])
            i_list[idx] = not i_list[idx]
            cursor.execute("UPDATE chess_state SET indiv_complete = ? WHERE player_id = ?", 
                           (json.dumps(i_list), player_id))
            return {"status": "updated"}

        return {"error": "Unknown action"}

    # --- SCORING ---
    def calculate_scores(self, cursor):
        """
        1. Calculate Group Pot: Sum of ALL completed Group Tasks from ALL players.
        """
        # Fetch all rows to sum up the pot
        all_rows = cursor.execute("SELECT group_tasks, group_complete, game_won FROM chess_state").fetchall()
        
        group_pot_earned = 0
        group_pot_max = 0
        
        # Calculate Pot
        for r in all_rows:
            g_tasks = json.loads(r['group_tasks'])
            g_complete = json.loads(r['group_complete'])
            
            for i, task in enumerate(g_tasks):
                pts = task['points']
                group_pot_max += pts
                if g_complete[i]:
                    group_pot_earned += pts

        # Mole Pot
        mole_pot_earned = group_pot_max - group_pot_earned

        # Distribute
        players = cursor.execute("SELECT id, is_mole FROM players").fetchall()
        for p in players:
            pid = p['id']
            # Get individual state
            st = cursor.execute("SELECT indiv_tasks, indiv_complete, game_won FROM chess_state WHERE player_id = ?", (pid,)).fetchone()
            
            i_tasks = json.loads(st['indiv_tasks'])
            i_complete = json.loads(st['indiv_complete'])
            game_won = bool(st['game_won'])
            
            personal_score = 0
            
            # A. Individual Challenges
            for i, task in enumerate(i_tasks):
                if i_complete[i]:
                    personal_score += task['points']
            
            # B. Chess Win Bonus
            if game_won:
                personal_score += 400
            
            # C. Add Pot
            if p['is_mole']:
                final_score = personal_score + mole_pot_earned
            else:
                final_score = personal_score + group_pot_earned
                
            cursor.execute("UPDATE players SET score = score + ? WHERE id = ?", (final_score, pid))