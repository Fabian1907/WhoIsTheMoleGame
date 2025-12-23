import random
import json

class RiskyBusiness:
    id = "risky-business"
    title = "Risky Business"
    duration = 20*60 
    max_points = 1600
    team_distribution = "Individual"
    description = """In this round, you will play a game of Risk, with some altered rules.
    The goal of the game for the group is to have as many troops alive at the end of the game as possible.

    The game ends after 20 minutes, or when everyone has taken 15 moves.
    
    
    Game setup:
    
    Roll a die to determine the turn order.
    Each player is dealt territory cards as normal, and places 2 troops on each of their territories.
    
    
    Game rules:
    
    In your turn you can choose between placing 2 new troops or attacking as many times as you want.
    The battles in the game work a bit differently:
    
    When attacking, if you have more attackers than there are defenders, you will always win.
    When your territory is being attacked, you can choose to move troops from the defending territory to any adjacent territory in your control.
    1 troop must always be left in a territory. You can also choose to move troops from 1 adjacent territory to the defending territory, in order to get more defenders.
    If an attack is set in motion, and after the move of the defenders, there are more attackers, you will remove all defenders, and lose 1 attacker for every 2 defenders, rounded down.
    If there are more defenders than attackers after the move, then the attack is lost, and all attackers perish. No defenders will be lost.
    
    Territory cards are not awarded after winning an attack.
    Troops cannot be moved around after attacking.
    
    A line is drawn between Eastern Australia and Venezuela.
    
    Continent bonuses work like normal.
    
    Each player will also have two hidden individual tasks that they will try to complete, two medium, one hard.
    
    
    Scoring:
    
    5 points per troop alive at the end of the game for the group.
    150 points for a medium task.
    300 points for a hard task.
    """
    
    medium_end_of_game_tasks = [
        "End the game with the most troops",
        "End the game with the least troops",
        "End the game with the most territories",
        "End the game with the least territories",
        "End the game with 35 troops +- 3",
        "End the game with 40 troops +- 3",
        "End the game with 45 troops +- 3",
        "End the game with 50 troops +- 3",
        "End the game with 55 troops +- 3",
        "End the game with 5 territories +- 1",
        "End the game with 8 territories +- 1",
        "End the game with 11 territories +- 1",
        "End the game with 14 territories +- 1",
        "End the game with 17 territories +- 1",
        "End the game in control of 1 continent",
    ]
    
    hard_end_of_game_tasks = [
        "End the game with the most troops but the least territories",
        "End the game with the least troops but the most territories",
        "End the game with the most troops and the most territories",
        "End the game with the least troops and the least territories",
        "End the game with 35 troops +- 1",
        "End the game with 40 troops +- 1",
        "End the game with 45 troops +- 1",
        "End the game with 50 troops +- 1",
        "End the game with 55 troops +- 1",
        "End the game with 5 territories",
        "End the game with 8 territories",
        "End the game with 11 territories",
        "End the game with 14 territories",
        "End the game with 17 territories",
        "End the game in control of 2 continents",
        "End the game in control of Africa",
        "End the game in control of North America",
        "End the game in control of Europe",
        "End the game in control of Australia and at least 14 territories in total",
        "End the game in control of South America and at least 14 territories in total",
    ]
    
    medium_tasks = [
        "Win 8 or more attacks",
        "Win 6 or less attacks",
        "Win 3 or more defenses",
        "Win 1 or less defenses",
        "Lose 6 or more attacks",
        
        "Destroy 11 or more defending troops in attacks",
        "Destroy 8 or less defending troops in attacks",
        "Lose 12 or more troops throughout the game",
        "Eliminate 5 or more enemy troops in a single turn",
        
        "Gain 7 troops from continent bonuses",
        "Break another player's continent bonus twice",
        "Gain 4 troops of continent bonus in one turn",
        
        "Control Africa at the end of any of your turns",
        "Control North America at the end of any of your turns",
        "Control Europe at the end of any of your turns",
        "Control Australia and South America each at the end of a turn (not necessarily the same turn)",
        
        "Have 13 or more troops on one territory",
        "Have 2 adjacent territories each with 8 or more troops",
        "Have 4 adjacent territories that all have only 1 troop",
        
        "Start your turn in control of 6 or fewer territories",
        "End your turn in control of 14 or more territories",
    ]
    
    hard_tasks = [
        "Win 13 or more attacks",
        "Win 3 or less attacks",
        "Win 6 or more defenses",
        "Win no defenses",
        "Lose 10 or more attacks",
        
        "Destroy 17 or more defending troops in attacks",
        "Destroy 5 or less defending troops in attacks",
        "Lose 20 or more troops throughout the game",
        "Eliminate 8 or more enemy troops in a single turn",
        
        "Gain 12 troops from continent bonuses",
        "Break another player's continent bonus 4 times",
        "Gain 7 troops of continent bonus in one turn",
        
        "Control Asia at the end of any of your turns",
        "Control Australia and Europe each at the end of a turn (not necessarily the same turn)",
        "Control Australia and North America each at the end of a turn (not necessarily the same turn)",
        "Control South America and Europe each at the end of a turn (not necessarily the same turn)",
        "Control South America and Africa each at the end of a turn (not necessarily the same turn)",
        "Control 3 different continents throughout the game, each held at the end of a turn",
        
        "Have 19 or more troops on one territory",
        "Have 3 adjacent territories each with 8 or more troops",
        "Have 6 adjacent territories that all have only 1 troop",
        
        "Start your turn in control of 3 or fewer territories",
        "End your turn in control of 19 or more territories",
    ]

    # --- SETUP ---
    def setup_db(self, cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS risk_state (
                player_id INTEGER PRIMARY KEY,
                tasks TEXT,      -- JSON list of {desc, points, type}
                complete TEXT    -- JSON list of booleans
            )
        """)

    # --- LOGIC ---
    def generate_secret_state(self, cursor):
        cursor.execute("DELETE FROM risk_state")
        players = cursor.execute("SELECT id, name FROM players").fetchall()
        
        # 1. Pool Management (Prevent repeats)
        pool_medium_end = list(self.medium_end_of_game_tasks)
        pool_hard_end = list(self.hard_end_of_game_tasks)
        pool_medium = list(self.medium_tasks)
        pool_hard = list(self.hard_tasks)
        
        random.shuffle(pool_medium_end)
        random.shuffle(pool_hard_end)
        random.shuffle(pool_medium)
        random.shuffle(pool_hard)
        
        mole_intel_data = {}

        for p in players:
            player_tasks = []
            
            # Logic: 1 End Game Task + 2 Others
            # Chance for Hard End Task
            if random.random() < 0.5 and pool_hard_end:
                # Scenario A: Hard End Task + 2 Mediums
                t1 = pool_hard_end.pop()
                player_tasks.append({"desc": t1, "points": 300, "type": "Hard (End Game)"})
                
                # Pick 2 Mediums
                player_tasks.append({"desc": pool_medium.pop(), "points": 150, "type": "Medium"})
                player_tasks.append({"desc": pool_medium.pop(), "points": 150, "type": "Medium"})
            else:
                # Scenario B: Medium End Task + 1 Medium + 1 Hard
                t1 = pool_medium_end.pop()
                player_tasks.append({"desc": t1, "points": 150, "type": "Medium (End Game)"})
                
                player_tasks.append({"desc": pool_medium.pop(), "points": 150, "type": "Medium"})
                player_tasks.append({"desc": pool_hard.pop(), "points": 300, "type": "Hard"})
            
            complete_init = [False] * 3
            
            cursor.execute("INSERT INTO risk_state (player_id, tasks, complete) VALUES (?, ?, ?)", 
                           (p['id'], json.dumps(player_tasks), json.dumps(complete_init)))
            
            # Mole Intel: One random task from this player
            random_intel = random.choice(player_tasks)
            mole_intel_data[p['id']] = {"name": p['name'], "task": random_intel['desc']}

        return mole_intel_data

    # --- TEXT GENERATORS ---
    def get_mole_text(self, dynamic_secret):
        txt = "SECRET INTEL (One random task from each player):\n"
        for pid, data in dynamic_secret.items():
            txt += f"\n👤 {data['name']}: {data['task']}"
        return txt

    def get_innocent_text(self, dynamic_secret):
        return "You are a team player. Coordinate with your team to have as many troops as possible. But don't forget about your own tasks"

    # --- VIEW ---
    def get_player_view(self, cursor, player_id, is_mole, dynamic_secret):
        row = cursor.execute("SELECT * FROM risk_state WHERE player_id = ?", (player_id,)).fetchone()
        
        tasks = json.loads(row['tasks'])
        complete = json.loads(row['complete'])
        
        view_tasks = []
        for i, t in enumerate(tasks):
            view_tasks.append({**t, "done": complete[i], "idx": i})
            
        view = {
            "game_id": self.id,
            "tasks": view_tasks
        }
        
        if is_mole:
            view['role_text'] = "Role: MOLE.\nSabotage troop counts. Complete your tasks."
        else:
            view['role_text'] = "Role: INNOCENT.\nKeep troops alive!"
            
        return view

    # --- INTERACTION --- 
    def handle_action(self, cursor, player_id, action, payload):
        if action == "toggle_task":
            idx = payload.get("index")
            row = cursor.execute("SELECT complete FROM risk_state WHERE player_id = ?", (player_id,)).fetchone()
            c_list = json.loads(row['complete'])
            c_list[idx] = not c_list[idx]
            cursor.execute("UPDATE risk_state SET complete = ? WHERE player_id = ?", (json.dumps(c_list), player_id))
            return {"status": "updated"}

        return {"error": "Unknown action"}

    # --- SCORING ---
    def calculate_scores(self, cursor):
        """
        Since we need the Game Master to input the total number of troops alive
        (5 points per troop), this calculation relies on the GM inputting that total 
        into the 'submit_score' field in the frontend.
        
        However, we CAN calculate the individual task points here.
        """
        # Fetch individual states
        rows = cursor.execute("SELECT player_id, tasks, complete FROM risk_state").fetchall()
        
        for r in rows:
            tasks = json.loads(r['tasks'])
            complete = json.loads(r['complete'])
            
            bonus_points = 0
            for i, t in enumerate(tasks):
                if complete[i]:
                    bonus_points += t['points']
            
            cursor.execute("UPDATE players SET score = score + ? WHERE id = ?", (bonus_points, r['player_id']))